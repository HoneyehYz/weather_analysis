import pandas as pd

WMO_DESCRIPTIONS = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Icy fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
    80: "Slight showers", 81: "Moderate showers", 82: "Violent showers",
    95: "Thunderstorm", 96: "Thunderstorm w/ hail", 99: "Thunderstorm w/ heavy hail",
}


def parse_forecast(raw: dict) -> pd.DataFrame:
    """Turn the Open-Meteo JSON response into a clean DataFrame."""
    hourly = raw["hourly"]
    df = pd.DataFrame(hourly)
    df["time"] = pd.to_datetime(df["time"])
    df = df.rename(columns={
        "temperature_2m": "temp_c",
        "apparent_temperature": "feels_like_c",
        "relative_humidity_2m": "humidity_pct",
        "precipitation": "precip_mm",
        "wind_speed_10m": "wind_kmh",
        "weather_code": "wmo_code",
        "cloud_cover": "cloud_pct",
    })
    df["condition"] = df["wmo_code"].map(WMO_DESCRIPTIONS).fillna("Unknown")
    df["date"] = df["time"].dt.date
    df = df.dropna(subset=["temp_c"])
    return df.reset_index(drop=True)


def daily_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate hourly data into per-day stats."""
    agg = df.groupby("date").agg(
        temp_min=("temp_c", "min"),
        temp_max=("temp_c", "max"),
        temp_avg=("temp_c", "mean"),
        feels_like_avg=("feels_like_c", "mean"),
        humidity_avg=("humidity_pct", "mean"),
        precip_total=("precip_mm", "sum"),
        wind_max=("wind_kmh", "max"),
        cloud_avg=("cloud_pct", "mean"),
    ).round(1)
    # dominant condition: most frequent WMO code per day
    dominant = (
        df.groupby("date")["condition"]
        .agg(lambda x: x.value_counts().idxmax())
    )
    agg["condition"] = dominant
    return agg.reset_index()


def build_llm_context(df: pd.DataFrame, daily: pd.DataFrame, location: str) -> str:
    """Build a concise text summary to feed to the LLM."""
    lines = [f"7-day hourly weather forecast for {location}.", ""]
    lines.append("Daily summary (all temps in °C, precipitation in mm, wind in km/h):")
    for _, row in daily.iterrows():
        lines.append(
            f"  {row['date']}: {row['condition']}, "
            f"temp {row['temp_min']}–{row['temp_max']}°C (avg {row['temp_avg']}°C), "
            f"precip {row['precip_total']} mm, wind max {row['wind_max']} km/h, "
            f"humidity {row['humidity_avg']}%"
        )
    lines.append("")
    overall_precip = daily["precip_total"].sum()
    lines.append(
        f"Overall: total precipitation {overall_precip:.1f} mm, "
        f"avg high {daily['temp_max'].mean():.1f}°C, "
        f"avg low {daily['temp_min'].mean():.1f}°C, "
        f"avg humidity {df['humidity_pct'].mean():.0f}%."
    )
    return "\n".join(lines)
