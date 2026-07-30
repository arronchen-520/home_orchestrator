from __future__ import annotations

import asyncio
import os
from datetime import datetime, timezone
from functools import lru_cache
from typing import Literal, TypedDict
from uuid import uuid4
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field, model_validator

ItemKind = Literal["event", "task", "note"]
ItemStatus = Literal["unclaimed", "claimed", "done"]


class ConfigurationError(RuntimeError):
    pass


class ItemDraft(BaseModel):
    kind: ItemKind = Field(
        description=(
            "event for a fixed-time or all-day occurrence; task for an action or chore; "
            "note for reference information"
        )
    )
    title: str = Field(min_length=1, max_length=120)
    details: str = Field(default="", max_length=2000)
    start_at: datetime | None = Field(
        default=None, description="Required for events; ISO 8601 with timezone"
    )
    end_at: datetime | None = Field(
        default=None, description="Optional event end; ISO 8601 with timezone"
    )
    due_at: datetime | None = Field(
        default=None, description="Optional task deadline; ISO 8601 with timezone"
    )
    all_day: bool = False

    @model_validator(mode="after")
    def match_kind(self) -> ItemDraft:
        if self.kind == "event":
            if self.start_at is None:
                raise ValueError("An event requires start_at")
            self.due_at = None
        elif self.kind == "task":
            self.start_at = self.end_at = None
            self.all_day = False
        else:
            self.start_at = self.end_at = self.due_at = None
            self.all_day = False
        return self


class BoardState(TypedDict, total=False):
    command: dict
    members: list[dict]
    items: list[dict]
    draft: dict | None
    result: dict


@lru_cache(maxsize=1)
def openrouter_chain():
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ConfigurationError("OPENROUTER_API_KEY is not configured")

    parser = PydanticOutputParser(pydantic_object=ItemDraft)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You classify short household board input in Chinese or English.

Rules:
- Preserve the language used by the person in title and details.
- event: an appointment, gathering, or occurrence at a fixed time or on a specific day.
- task: an action, chore, request, or shopping item. A task may have a deadline.
- note: reference information with no action to perform.
- Resolve relative dates using the supplied current time and IANA timezone.
- Never invent an owner or assignee.
- Keep the title concise and put remaining useful text in details.

{format_instructions}""",
            ),
            (
                "human",
                "Current time: {now}\nTimezone: {timezone_name}\nInput: {text}",
            ),
        ]
    ).partial(format_instructions=parser.get_format_instructions())
    model = ChatOpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
        model=os.getenv("OPENROUTER_MODEL", "openrouter/free"),
        temperature=0,
        default_headers={"X-OpenRouter-Title": "Home Orchestrator"},
    )
    return prompt | model | parser


async def parse_with_openrouter(text: str, now: str, timezone_name: str) -> ItemDraft:
    return await openrouter_chain().ainvoke(
        {"text": text, "now": now, "timezone_name": timezone_name}
    )


def _member_ids(state: BoardState) -> set[str]:
    return {member["id"] for member in state.get("members", [])}


def _require_actor(state: BoardState, actor_id: str | None) -> str:
    if not actor_id or actor_id not in _member_ids(state):
        raise ValueError("Choose a valid family member first")
    return actor_id


def _find_item(items: list[dict], item_id: str) -> tuple[int, dict]:
    for index, item in enumerate(items):
        if item["id"] == item_id:
            return index, item
    raise ValueError("Item not found")


def route_command(state: BoardState) -> str:
    command_type = state["command"].get("type")
    routes = {
        "add_item": "parse_item",
        "add_member": "add_member",
        "update_item": "update_item",
        "delete_item": "delete_item",
    }
    if command_type not in routes:
        raise ValueError("Unsupported command")
    return routes[command_type]


async def parse_item_node(state: BoardState) -> dict:
    command = state["command"]
    timezone_name = command.get("timezone", "UTC")
    try:
        local_now = datetime.now(ZoneInfo(timezone_name))
    except ZoneInfoNotFoundError as exc:
        raise ValueError("Invalid timezone") from exc
    draft = await parse_with_openrouter(
        command["text"], local_now.isoformat(), timezone_name
    )
    return {"draft": draft.model_dump(mode="json")}


def save_item_node(state: BoardState) -> dict:
    command = state["command"]
    actor_id = _require_actor(state, command.get("actor_id"))
    owner_id = command.get("owner_id")
    if owner_id is not None and owner_id not in _member_ids(state):
        raise ValueError("Invalid owner")

    draft = ItemDraft.model_validate(state["draft"])
    actionable = draft.kind != "note"
    item = {
        "id": str(uuid4()),
        **draft.model_dump(mode="json"),
        "owner_id": owner_id if actionable else None,
        "status": ("claimed" if owner_id else "unclaimed") if actionable else None,
        "created_by": actor_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    return {
        "items": [*state.get("items", []), item],
        "draft": None,
        "result": {"action": "created", "item_id": item["id"]},
    }


def add_member_node(state: BoardState) -> dict:
    name = state["command"].get("name", "").strip()
    if not name or len(name) > 40:
        raise ValueError("Member name must be 1 to 40 characters")
    members = state.get("members", [])
    if any(member["name"].casefold() == name.casefold() for member in members):
        raise ValueError("That family member already exists")
    member = {"id": str(uuid4()), "name": name}
    return {
        "members": [*members, member],
        "result": {"action": "member_added", "member_id": member["id"]},
    }


def update_item_node(state: BoardState) -> dict:
    command = state["command"]
    actor_id = _require_actor(state, command.get("actor_id"))
    fields = command.get("fields", {})
    if not fields or set(fields) - {"owner_id", "status"}:
        raise ValueError("Only owner and status can be changed")

    items = [dict(item) for item in state.get("items", [])]
    index, item = _find_item(items, command["item_id"])
    if item["kind"] == "note":
        raise ValueError("Notes do not have owners or status")

    if "owner_id" in fields:
        owner_id = fields["owner_id"]
        if owner_id is not None and owner_id not in _member_ids(state):
            raise ValueError("Invalid owner")
        item["owner_id"] = owner_id
        if item["status"] != "done":
            item["status"] = "claimed" if owner_id else "unclaimed"

    if "status" in fields:
        status = fields["status"]
        if status not in {"unclaimed", "claimed", "done"}:
            raise ValueError("Invalid status")
        if status == "unclaimed":
            item["owner_id"] = None
        elif not item["owner_id"]:
            item["owner_id"] = actor_id
        item["status"] = status

    items[index] = item
    return {
        "items": items,
        "result": {"action": "updated", "item_id": item["id"]},
    }


def delete_item_node(state: BoardState) -> dict:
    command = state["command"]
    _require_actor(state, command.get("actor_id"))
    items = list(state.get("items", []))
    index, item = _find_item(items, command["item_id"])
    del items[index]
    return {
        "items": items,
        "result": {"action": "deleted", "item_id": item["id"]},
    }


def build_graph(checkpointer):
    builder = StateGraph(BoardState)
    builder.add_node("parse_item", parse_item_node)
    builder.add_node("save_item", save_item_node)
    builder.add_node("add_member", add_member_node)
    builder.add_node("update_item", update_item_node)
    builder.add_node("delete_item", delete_item_node)
    builder.add_conditional_edges(
        START,
        route_command,
        {
            "parse_item": "parse_item",
            "add_member": "add_member",
            "update_item": "update_item",
            "delete_item": "delete_item",
        },
    )
    builder.add_edge("parse_item", "save_item")
    builder.add_edge("save_item", END)
    builder.add_edge("add_member", END)
    builder.add_edge("update_item", END)
    builder.add_edge("delete_item", END)
    return builder.compile(checkpointer=checkpointer)


class BoardService:
    def __init__(self, checkpointer, thread_id: str = "family-default"):
        self.graph = build_graph(checkpointer)
        self.config = {"configurable": {"thread_id": thread_id}}
        # ponytail: one-process lock; move board rows to transactional storage for multi-worker use.
        self._lock = asyncio.Lock()

    async def get_board(self) -> dict:
        snapshot = await self.graph.aget_state(self.config)
        values = snapshot.values or {}
        return {
            "members": values.get("members", []),
            "items": values.get("items", []),
            "result": values.get("result"),
        }

    async def execute(self, command: dict) -> dict:
        async with self._lock:
            await self.graph.ainvoke({"command": command}, self.config)
            return await self.get_board()
