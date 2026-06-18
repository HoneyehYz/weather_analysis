# Weather Data Analyzer Dashboard

<img width="1781" height="953" alt="Screenshot 2026-06-18 at 4 18 08 PM" src="https://github.com/user-attachments/assets/aecad814-aa30-4e77-ba24-7b6d7c1eee49" />

An interactive weather dashboard that fetches real-time 7-day forecasts, visualizes the data with charts, and uses an LLM to explain the weather pattern in plain English.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue) ![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-red) ![License](https://img.shields.io/badge/license-MIT-green)

---

## Features

- **Live forecast data** — pulls 7 days of hourly weather from [Open-Meteo](https://open-meteo.com/)
- **Interactive charts** — temperature, feels-like, humidity, and wind speed visualized with Plotly
- **Daily summary table** — min/max/avg temperature, precipitation totals, dominant condition per day
- **LLM analysis** — sends the forecast summary to OpenAI and returns a plain-English explanation of the week's weather pattern
- **City search** — geocode any city by name; defaults to Ottawa

---

## Tech Stack

| Layer | Tool |
|---|---|
| Dashboard | Streamlit |
| Charts | Plotly |
| Data | pandas |
| Weather API | Open-Meteo |
| LLM | OpenAI (`gpt-4o-mini`) |

---

## Project Structure

```
weather_analysis/
├── app.py              # Streamlit dashboard (entry point)
├── weather_api.py      # Open-Meteo geocoding + forecast fetch
├── data_processor.py   # pandas cleaning, daily aggregation, LLM context builder
├── llm_analyzer.py     # OpenAI chat completion wrapper
├── requirements.txt
└── .env.example
```

---

## Getting Started

### 1. Clone and install

```bash
git clone https://github.com/your-username/weather-dashboard.git
cd weather-dashboard
pip install -r requirements.txt
```

### 2. Add your OpenAI key

```bash
cp .env.example .env
# open .env and paste your key
```

Or skip this step and enter the key directly in the dashboard sidebar — the weather charts work without it.

### 3. Run

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---

## Usage

1. Type any city name in the sidebar and click **Fetch Forecast**
2. Toggle the charts you want to see (Temperature, Humidity, Wind Speed)
3. Scroll down to the **LLM Weather Analysis** section and click **Generate Analysis** for a plain-English forecast summary

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `OPENAI_API_KEY` | For LLM only | — | Your OpenAI API key |
| `OPENAI_MODEL` | No | `gpt-4o-mini` | Any OpenAI chat model ID |


