import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from board_graph import BoardService, ItemDraft


class BoardFlowTest(unittest.IsolatedAsyncioTestCase):
    async def test_bilingual_items_status_and_restart_persistence(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            database = str(Path(temp_dir) / "test.sqlite3")
            async with AsyncSqliteSaver.from_conn_string(database) as saver:
                await saver.setup()
                service = BoardService(saver, "test-family")
                board = await service.execute({"type": "add_member", "name": "小林"})
                actor_id = board["members"][0]["id"]

                drafts = AsyncMock(
                    side_effect=[
                        ItemDraft(kind="task", title="买牛奶"),
                        ItemDraft(
                            kind="event",
                            title="Dentist appointment",
                            start_at="2026-08-01T15:00:00-04:00",
                        ),
                        ItemDraft(kind="note", title="Wi-Fi", details="Guest password"),
                    ]
                )
                with patch("board_graph.parse_with_openrouter", drafts):
                    for text in ("买牛奶", "Dentist Saturday at 3", "Wi-Fi info"):
                        board = await service.execute(
                            {
                                "type": "add_item",
                                "text": text,
                                "actor_id": actor_id,
                                "timezone": "America/Toronto",
                            }
                        )

                task, event, note = board["items"]
                self.assertEqual(
                    [task["kind"], event["kind"], note["kind"]],
                    ["task", "event", "note"],
                )
                self.assertEqual(task["status"], "unclaimed")
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

            async with AsyncSqliteSaver.from_conn_string(database) as saver:
                await saver.setup()
                restored = await BoardService(saver, "test-family").get_board()
                self.assertEqual(len(restored["items"]), 3)
                self.assertEqual(restored["items"][0]["status"], "claimed")


if __name__ == "__main__":
    unittest.main()
