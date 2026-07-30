import sqlite3
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import AsyncMock, patch

from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from board_db import BoardDatabase
from board_graph import BoardService, ExtractionResult, ItemDraft


class BoardFlowTest(unittest.IsolatedAsyncioTestCase):
    async def test_multi_item_input_original_text_and_restart_persistence(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = str(Path(temp_dir) / "test.sqlite3")
            database = BoardDatabase(database_path)
            database.setup()
            async with AsyncSqliteSaver.from_conn_string(database_path) as saver:
                await saver.setup()
                service = BoardService(database, saver, "test-family")
                board = await service.execute(
                    {"type": "add_member", "name": "小林"}
                )
                actor_id = board["members"][0]["id"]
                original_text = (
                    "周六买牛奶，每月最后一天下午三点看牙医，再记下 Wi-Fi 密码"
                )
                extraction = ExtractionResult(
                    items=[
                        ItemDraft(
                            kind="task",
                            title="买牛奶",
                            due_date="2026-08-01",
                        ),
                        ItemDraft(
                            kind="event",
                            title="Dentist appointment",
                            start_at="2026-08-31T15:00:00-04:00",
                            recurrence="monthly",
                            monthly_on_last_day=True,
                            recurrence_until="2026-11-30",
                        ),
                        ItemDraft(
                            kind="note",
                            title="Wi-Fi",
                            details="Guest password",
                        ),
                    ]
                )
                with patch(
                    "board_graph.parse_with_openrouter",
                    AsyncMock(return_value=extraction),
                ):
                    board = await service.execute(
                        {
                            "type": "add_item",
                            "text": original_text,
                            "actor_id": actor_id,
                            "timezone": "America/Toronto",
                            "source": "text",
                        }
                    )

                task, event, note = board["items"]
                self.assertEqual(
                    [task["kind"], event["kind"], note["kind"]],
                    ["task", "event", "note"],
                )
                self.assertEqual(task["due_date"], "2026-08-01")
                self.assertEqual(event["start_at"], "2026-08-31T15:00:00-04:00")
                self.assertEqual(event["recurrence"], "monthly")
                self.assertTrue(event["monthly_on_last_day"])
                self.assertEqual(event["recurrence_until"], "2026-11-30")
                self.assertEqual(
                    {item["original_text"] for item in board["items"]},
                    {original_text},
                )
                self.assertEqual(len(board["result"]["item_ids"]), 3)
                self.assertIsNone(note["status"])

                board = await service.execute(
                    {
                        "type": "update_item",
                        "item_id": task["id"],
                        "actor_id": actor_id,
                        "fields": {"status": "claimed"},
                    }
                )
                self.assertEqual(board["items"][0]["owner_id"], actor_id)

                await service.execute(
                    {
                        "type": "update_occurrence",
                        "item_id": event["id"],
                        "occurrence_date": "2026-09-30",
                        "actor_id": actor_id,
                        "fields": {
                            "title": "Moved dentist",
                            "start_at": "2026-10-01T16:00:00-04:00",
                        },
                    }
                )
                await service.execute(
                    {
                        "type": "cancel_occurrence",
                        "item_id": event["id"],
                        "occurrence_date": "2026-10-31",
                        "actor_id": actor_id,
                    }
                )
                calendar = await service.get_calendar(
                    date(2026, 8, 1), date(2026, 12, 31)
                )
                occurrences = [
                    item for item in calendar["items"] if item["kind"] == "event"
                ]
                self.assertEqual(
                    [item["start_at"][:10] for item in occurrences],
                    ["2026-08-31", "2026-10-01", "2026-11-30"],
                )
                self.assertEqual(occurrences[1]["title"], "Moved dentist")
                self.assertEqual(occurrences[1]["occurrence_date"], "2026-09-30")
            database.close()

            database = BoardDatabase(database_path)
            database.setup()
            restored = database.get_board("test-family")
            self.assertEqual(len(restored["items"]), 3)
            self.assertEqual(restored["items"][0]["status"], "claimed")
            self.assertTrue(restored["items"][1]["monthly_on_last_day"])
            restored_calendar = database.get_calendar(
                "test-family", date(2026, 8, 1), date(2026, 12, 31)
            )
            self.assertEqual(
                [
                    item["start_at"][:10]
                    for item in restored_calendar["items"]
                    if item["kind"] == "event"
                ],
                ["2026-08-31", "2026-10-01", "2026-11-30"],
            )
            database.close()

            connection = sqlite3.connect(database_path)
            try:
                self.assertEqual(
                    connection.execute("SELECT COUNT(*) FROM items").fetchone()[0],
                    3,
                )
            finally:
                connection.close()

    def test_recurrence_is_limited_to_events(self):
        with self.assertRaisesRegex(ValueError, "Only events can recur"):
            ItemDraft(kind="task", title="Take out trash", recurrence="weekly")
        with self.assertRaisesRegex(ValueError, "must start on a month's last day"):
            ItemDraft(
                kind="event",
                title="Month end",
                start_date="2026-02-27",
                recurrence="monthly",
                monthly_on_last_day=True,
            )


if __name__ == "__main__":
    unittest.main()
