import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from test_support import TestBoardDatabase as BoardDatabase
from weather import FORECAST_URL, GEOCODING_URL, WeatherService


def forecast_payload() -> dict:
    entries = []
    start = datetime.fromisoformat("2026-07-30T00:00:00-04:00")
    for day_index in range(5):
        for hour, temperature, description in (
            (9, day_index + 10, "morning"),
            (12, day_index + 16, "clear sky"),
            (18, day_index + 14, "evening"),
        ):
            local = start + timedelta(days=day_index, hours=hour)
            entries.append(
                {
                    "dt": int(local.timestamp()),
                    "main": {
                        "temp_min": temperature - 1,
                        "temp_max": temperature + 1,
                    },
                    "weather": [{"description": description, "icon": "01d"}],
                    "pop": 0.4 if hour == 18 else 0.1,
                }
            )
    return {"city": {"timezone": -4 * 60 * 60}, "list": entries}


class FakeWeatherService(WeatherService):
    def __init__(self):
        super().__init__("test-key")
        self.forecast_calls = 0

    async def _get_json(self, url: str, params: dict) -> dict | list:
        if url == GEOCODING_URL:
            return [
                {
                    "name": "Toronto",
                    "country": "CA",
                    "lat": 43.6532,
                    "lon": -79.3832,
                }
            ]
        if url == FORECAST_URL:
            self.forecast_calls += 1
            return forecast_payload()
        raise AssertionError(url)


class WeatherFlowTest(unittest.IsolatedAsyncioTestCase):
    async def test_city_persistence_five_day_aggregation_and_cache(self):
        weather = FakeWeatherService()
        location = await weather.geocode("Toronto, CA")

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "board.sqlite3"
            database = BoardDatabase(path)
            database.setup()
            database.set_household_location("test-family", location)
            database.close()

            database = BoardDatabase(path)
            database.setup()
            restored = database.get_weather_location("test-family")
            database.close()

        first = await weather.forecast(restored, "en")
        second = await weather.forecast(restored, "en")

        self.assertEqual(restored["city"], "Toronto")
        self.assertEqual(len(first["days"]), 5)
        self.assertEqual(first["days"][0]["date"], "2026-07-30")
        self.assertEqual(first["days"][0]["description"], "clear sky")
        self.assertEqual(first["days"][0]["temp_min"], 9)
        self.assertEqual(first["days"][0]["temp_max"], 17)
        self.assertEqual(first["days"][0]["precipitation_probability"], 40)
        self.assertIs(first, second)
        self.assertEqual(weather.forecast_calls, 1)


if __name__ == "__main__":
    unittest.main()
