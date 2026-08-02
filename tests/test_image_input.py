import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException

from backend.hearthbook.api.conversation import describe_image


class Upload:
    content_type = "image/png"

    def __init__(self, data):
        self.data = data

    async def read(self, _size=None):
        return self.data


class ImageInputTest(unittest.IsolatedAsyncioTestCase):
    async def test_png_without_a_note_is_described(self):
        response = SimpleNamespace(content="9月12日学校活动")
        with patch("backend.hearthbook.api.conversation.model", return_value=SimpleNamespace(ainvoke=AsyncMock(return_value=response))):
            summary = await describe_image(Upload(b"\x89PNG\r\n\x1a\nimage"), "", "zh")

        self.assertEqual(summary, "9月12日学校活动")

    async def test_non_png_is_rejected_before_the_model_call(self):
        upload = Upload(b"not a png")
        with self.assertRaisesRegex(HTTPException, "valid PNG"):
            await describe_image(upload, "", "en")


if __name__ == "__main__":
    unittest.main()
