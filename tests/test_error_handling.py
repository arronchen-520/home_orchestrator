import unittest
from types import SimpleNamespace

from fastapi import HTTPException

from backend.hearthbook.api.errors import service_call
from backend.hearthbook.llm.graph import ConfigurationError


class ErrorHandlingTest(unittest.IsolatedAsyncioTestCase):
    async def test_provider_configuration_error_is_safe_and_contextual(self):
        async def fail():
            raise ConfigurationError("OPENROUTER_API_KEY is not configured")

        request = SimpleNamespace(
            url=SimpleNamespace(path="/api/messages"),
            state=SimpleNamespace(
                household_id="family-1", session_id="session-1", user_id="user-1"
            ),
        )
        with self.assertLogs("backend.hearthbook.api.errors", level="ERROR") as captured:
            with self.assertRaises(HTTPException) as raised:
                await service_call(fail(), request, "text message")

        self.assertEqual(raised.exception.status_code, 503)
        self.assertEqual(raised.exception.detail, {"code": "service_unavailable"})
        self.assertIn("operation=text message", captured.output[0])
        self.assertIn("household_id=family-1", captured.output[0])


if __name__ == "__main__":
    unittest.main()
