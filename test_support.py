from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

from board_db import BoardDatabase, _now


STORES: dict[str, dict[str, list[dict]]] = {}


def _columns(value: str) -> list[str]:
    result, current, depth = [], "", 0
    for char in value:
        depth += char == "("
        depth -= char == ")"
        if char == "," and depth == 0:
            result.append(current)
            current = ""
        else:
            current += char
    return result + [current]


class FakeQuery:
    def __init__(self, client, table: str):
        self.client = client
        self.table = table
        self.action = "select"
        self.columns = "*"
        self.payload = None
        self.filters = []
        self.orders = []
        self.maximum = None
        self.conflicts = []

    def select(self, columns="*"):
        self.action, self.columns = "select", columns
        return self

    def insert(self, payload):
        self.action, self.payload = "insert", payload
        return self

    def update(self, payload):
        self.action, self.payload = "update", payload
        return self

    def delete(self):
        self.action = "delete"
        return self

    def upsert(self, payload, on_conflict=""):
        self.action, self.payload = "upsert", payload
        self.conflicts = on_conflict.split(",") if on_conflict else ["id"]
        return self

    def eq(self, key, value):
        self.filters.append(lambda row, k=key, v=value: row.get(k) == v)
        return self

    def is_(self, key, value):
        self.filters.append(
            lambda row, k=key, v=value: row.get(k) is None
            if v == "null"
            else row.get(k) is v
        )
        return self

    def in_(self, key, values):
        self.filters.append(lambda row, k=key, v=set(values): row.get(k) in v)
        return self

    def order(self, key):
        self.orders.append(key)
        return self

    def limit(self, maximum):
        self.maximum = maximum
        return self

    def _matched(self):
        return [
            row
            for row in self.client.store[self.table]
            if all(check(row) for check in self.filters)
        ]

    def execute(self):
        table = self.client.store[self.table]
        if self.action == "insert":
            values = self.payload if isinstance(self.payload, list) else [self.payload]
            for value in values:
                row = deepcopy(value)
                if self.table == "chat_messages" and "id" not in row:
                    row["id"] = self.client.next_message_id()
                table.append(row)
            return SimpleNamespace(data=deepcopy(values))

        matched = self._matched()
        if self.action == "update":
            for row in matched:
                row.update(deepcopy(self.payload))
            return SimpleNamespace(data=deepcopy(matched))
        if self.action == "delete":
            for row in matched:
                table.remove(row)
            return SimpleNamespace(data=deepcopy(matched))
        if self.action == "upsert":
            values = self.payload if isinstance(self.payload, list) else [self.payload]
            saved = []
            for value in values:
                existing = next(
                    (
                        row
                        for row in table
                        if all(row.get(key) == value.get(key) for key in self.conflicts)
                    ),
                    None,
                )
                if existing:
                    existing.update(deepcopy(value))
                    saved.append(existing)
                else:
                    table.append(deepcopy(value))
                    saved.append(table[-1])
            return SimpleNamespace(data=deepcopy(saved))

        for key in reversed(self.orders):
            matched.sort(key=lambda row, k=key: row.get(k) or "")
        if self.maximum is not None:
            matched = matched[: self.maximum]
        return SimpleNamespace(data=[self._project(row) for row in matched])

    def _project(self, row):
        if self.columns == "*":
            return deepcopy(row)
        result = {}
        for column in _columns(self.columns):
            if column == "submissions(original_text)":
                result["submissions"] = next(
                    (
                        {"original_text": submission["original_text"]}
                        for submission in self.client.store["submissions"]
                        if submission["id"] == row.get("submission_id")
                    ),
                    None,
                )
            else:
                result[column] = deepcopy(row.get(column))
        return result


class FakeClient:
    def __init__(self, store):
        self.store = store

    def table(self, name):
        return FakeQuery(self, name)

    def next_message_id(self):
        rows = self.store["chat_messages"]
        return max((row["id"] for row in rows), default=0) + 1

    def rpc(self, name, params):
        if name == "create_chat_session":
            session = deepcopy(params["session_data"])
            session.setdefault("owner_id", None)
            session.setdefault("clarification_count", 0)
            session.setdefault("payload_json", "{}")
            self.store["chat_sessions"].append(session)
            self.store["chat_messages"].append(
                {
                    "id": self.next_message_id(),
                    "session_id": session["id"],
                    "role": "user",
                    "content": params["first_message"],
                    "created_at": session["created_at"],
                }
            )
            data = None
        elif name == "append_chat_message":
            self.store["chat_messages"].append(
                {
                    "id": self.next_message_id(),
                    "session_id": params["target_session_id"],
                    "role": params["message_role"],
                    "content": params["message_content"],
                    "created_at": params["now_text"],
                }
            )
            session = next(
                row
                for row in self.store["chat_sessions"]
                if row["id"] == params["target_session_id"]
            )
            session["updated_at"] = params["now_text"]
            data = None
        elif name == "create_board_items":
            household = next(
                row
                for row in self.store["households"]
                if row["id"] == params["target_household_id"]
            )
            household["timezone"] = params["target_timezone"]
            submission = params["submission_data"]
            if not any(
                row["id"] == submission["id"] for row in self.store["submissions"]
            ):
                self.store["submissions"].append(deepcopy(submission))
            for item in params["item_data"]:
                if not any(
                    row.get("submission_id") == item["submission_id"]
                    and row.get("source_index") == item["source_index"]
                    for row in self.store["items"]
                ):
                    self.store["items"].append(deepcopy(item))
            data = [
                row["id"]
                for row in sorted(
                    self.store["items"], key=lambda value: value.get("source_index", 0)
                )
                if row.get("submission_id") == submission["id"]
            ]
        else:
            raise AssertionError(name)
        return SimpleNamespace(execute=lambda: SimpleNamespace(data=data))


class TestBoardDatabase(BoardDatabase):
    __test__ = False

    def __init__(self, path: str | Path):
        key = str(Path(path).resolve())
        store = STORES.setdefault(
            key,
            {
                name: []
                for name in (
                    "households",
                    "household_memberships",
                    "members",
                    "submissions",
                    "items",
                    "recurrence_exceptions",
                    "chat_sessions",
                    "chat_messages",
                )
            },
        )
        super().__init__(FakeClient(store))

    def setup(self) -> None:
        self.ensure_household("test-family")

    def ensure_household(
        self, household_id: str, timezone_name: str = "UTC"
    ) -> None:
        if not any(
            row["id"] == household_id
            for row in self.client.store["households"]
        ):
            self.client.store["households"].append(
                {
                    "id": household_id,
                    "name": household_id,
                    "invite_code": uuid4().hex[:12],
                    "timezone": timezone_name,
                    "city": None,
                    "country_code": None,
                    "latitude": None,
                    "longitude": None,
                    "memory": "",
                    "created_at": _now(),
                }
            )
