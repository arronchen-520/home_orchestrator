import unittest

from pydantic import ValidationError

from backend.hearthbook.api.notifications import PushSubscriptionInput


class NotificationInputTest(unittest.TestCase):
    def test_push_endpoint_must_use_https(self):
        with self.assertRaises(ValidationError):
            PushSubscriptionInput(
                endpoint="http://push.example.test/send",
                keys={"p256dh": "p" * 20, "auth": "a" * 8},
                timezone="UTC",
            )


if __name__ == "__main__":
    unittest.main()
