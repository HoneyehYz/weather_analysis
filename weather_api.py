import requests
from typing import Optional

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

HOURLY_VARIABLES = [
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation",
    "wind_speed_10m",
    "apparent_temperature",
    "weather_code",
    "cloud_cover",
]


def geocode_city(city: str) -> Optional[dict]:
    """Return {name, latitude, longitude, country} for the first geocoding hit."""
    resp = requests.get(
        GEOCODE_URL,
        params={"name": city, "count": 1, "language": "en", "format": "json"},
        timeout=10,
    )
    resp.raise_for_status()
    results = resp.json().get("results")
    if not results:
        return None
    r = results[0]
    return {
        "name": r.get("name", city),
        "country": r.get("country", ""),
        "latitude": r["latitude"],
        "longitude": r["longitude"],
    }


def fetch_forecast(latitude: float, longitude: float) -> dict:
    """Fetch 7-day hourly forecast from Open-Meteo."""
    resp = requests.get(
        FORECAST_URL,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "hourly": ",".join(HOURLY_VARIABLES),
            "wind_speed_unit": "kmh",
            "timezone": "auto",
            "forecast_days": 7,
        },
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()
