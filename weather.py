from __future__ import annotations

import time
from collections import defaultdict
from datetime import datetime, timedelta, timezone

import httpx

GEOCODING_URL = "https://api.openweathermap.org/geo/1.0/direct"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
CACHE_SECONDS = 6 * 60 * 60


class WeatherConfigurationError(RuntimeError):
    pass


class WeatherProviderError(RuntimeError):
    pass


class WeatherService:
    def __init__(self, api_key: str | None):
        self.api_key = api_key
        self._cache: dict[tuple[float, float, str], tuple[float, dict]] = {}

    def _require_key(self) -> str:
        if not self.api_key:
            raise WeatherConfigurationError("OPENWEATHER_API_KEY is not configured")
        return self.api_key

    async def _get_json(self, url: str, params: dict) -> dict | list:
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
        except (httpx.HTTPError, ValueError) as exc:
            # Do not include the provider URL in the public error; it contains the key.
            raise WeatherProviderError("OpenWeather request failed") from exc

    async def geocode(self, query: str) -> dict:
        results = await self._get_json(
            GEOCODING_URL,
            {"q": query.strip(), "limit": 1, "appid": self._require_key()},
        )
        if not isinstance(results, list) or not results:
            raise ValueError("City not found")
        result = results[0]
        return {
            "city": result["name"],
            "country_code": result["country"],
            "latitude": float(result["lat"]),
            "longitude": float(result["lon"]),
        }

    async def forecast(self, location: dict, language: str) -> dict:
        key = (
            round(location["latitude"], 4),
            round(location["longitude"], 4),
            language,
        )
        cached = self._cache.get(key)
        if cached and time.monotonic() - cached[0] < CACHE_SECONDS:
            return cached[1]

        try:
            payload = await self._get_json(
                FORECAST_URL,
                {
                    "lat": location["latitude"],
                    "lon": location["longitude"],
                    "units": "metric",
                    "lang": language,
                    "appid": self._require_key(),
                },
            )
            result = {
                "location": {
                    "city": location["city"],
                    "country_code": location["country_code"],
                },
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "stale": False,
                "days": aggregate_forecast(payload),
            }
        except WeatherProviderError:
            if cached:
                return {**cached[1], "stale": True}
            raise

        self._cache[key] = (time.monotonic(), result)
        return result

    def clear_cache(self) -> None:
        self._cache.clear()


def aggregate_forecast(payload: dict | list) -> list[dict]:
    if not isinstance(payload, dict) or not isinstance(payload.get("list"), list):
        raise WeatherProviderError("OpenWeather returned invalid forecast data")

    offset = int(payload.get("city", {}).get("timezone", 0))
    grouped: dict[str, list[tuple[datetime, dict]]] = defaultdict(list)
    for entry in payload["list"]:
        local_time = datetime.fromtimestamp(entry["dt"], timezone.utc) + timedelta(
            seconds=offset
        )
        grouped[local_time.date().isoformat()].append((local_time, entry))

    days = []
    for date_key in sorted(grouped)[:5]:
        entries = grouped[date_key]
        representative = min(
            entries,
            key=lambda pair: abs(
                pair[0].hour + pair[0].minute / 60 - 12
            ),
        )[1]
        condition = (representative.get("weather") or [{}])[0]
        days.append(
            {
                "date": date_key,
                "temp_min": round(
                    min(entry["main"]["temp_min"] for _, entry in entries)
                ),
                "temp_max": round(
                    max(entry["main"]["temp_max"] for _, entry in entries)
                ),
                "description": condition.get("description", ""),
                "icon": condition.get("icon", ""),
                "precipitation_probability": round(
                    max(float(entry.get("pop", 0)) for _, entry in entries) * 100
                ),
            }
        )
    if not days:
        raise WeatherProviderError("OpenWeather returned no forecast days")
    return days
