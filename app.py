import os
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from dotenv import load_dotenv

from weather_api import geocode_city, fetch_forecast
from data_processor import parse_forecast, daily_summary, build_llm_context
from llm_analyzer import analyze_weather

load_dotenv()

st.set_page_config(
    page_title="Weather Analyzer",
    page_icon="🌤",
    layout="wide",
)

# ── Sidebar ────────────────────────────────────────────────────────────────────
st.sidebar.title("🌤 Weather Analyzer")
city_input = st.sidebar.text_input("City", value="Ottawa", placeholder="e.g. Tokyo")
run_btn = st.sidebar.button("Fetch Forecast", type="primary", use_container_width=True)

st.sidebar.divider()
st.sidebar.markdown("**Charts to display**")
show_temp = st.sidebar.checkbox("Temperature", value=True)
show_feels = st.sidebar.checkbox("Feels-like temperature", value=True)
show_humidity = st.sidebar.checkbox("Humidity", value=True)
show_wind = st.sidebar.checkbox("Wind speed", value=True)

st.sidebar.divider()
openai_key = st.sidebar.text_input(
    "OpenAI API Key",
    type="password",
    value=os.environ.get("OPENAI_API_KEY", ""),
    help="Required only for the LLM analysis section.",
)
llm_model = st.sidebar.selectbox(
    "LLM model",
    ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo"],
    index=0,
)

# ── Session state init ─────────────────────────────────────────────────────────
if "weather_data" not in st.session_state:
    st.session_state.weather_data = None
if "llm_analysis" not in st.session_state:
    st.session_state.llm_analysis = None

# ── Main area ──────────────────────────────────────────────────────────────────
st.title("Weather Data Analyzer Dashboard")
st.caption("Powered by Open-Meteo (free, no API key) · LLM analysis via OpenAI")

# ── Data fetching ──────────────────────────────────────────────────────────────
if run_btn:
    st.session_state.llm_analysis = None  # reset analysis on new fetch
    with st.spinner(f"Fetching forecast for **{city_input}**…"):
        try:
            location = geocode_city(city_input)
        except Exception as e:
            st.error(f"Geocoding failed: {e}")
            st.stop()

        if location is None:
            st.error(f"Could not find city '{city_input}'. Try a different spelling.")
            st.stop()

        try:
            raw = fetch_forecast(location["latitude"], location["longitude"])
        except Exception as e:
            st.error(f"Weather API error: {e}")
            st.stop()

        df = parse_forecast(raw)
        daily = daily_summary(df)
        st.session_state.weather_data = {
            "df": df,
            "daily": daily,
            "label": f"{location['name']}, {location['country']}",
        }

if st.session_state.weather_data is None:
    st.info("Enter a city name in the sidebar and click **Fetch Forecast** to begin.")
    st.stop()

df = st.session_state.weather_data["df"]
daily = st.session_state.weather_data["daily"]
label = st.session_state.weather_data["label"]

st.success(f"Showing 7-day forecast for **{label}**")

# ── KPI row ────────────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("Avg High", f"{daily['temp_max'].mean():.1f} °C")
col2.metric("Avg Low", f"{daily['temp_min'].mean():.1f} °C")
col3.metric("Total Rain", f"{daily['precip_total'].sum():.1f} mm")
col4.metric("Avg Humidity", f"{df['humidity_pct'].mean():.0f} %")

st.divider()

# ── Charts ─────────────────────────────────────────────────────────────────────
def hourly_line(y_col: str, label: str, color: str, unit: str) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["time"], y=df[y_col],
        mode="lines", name=label,
        line=dict(color=color, width=2),
        fill="tozeroy", fillcolor=color.replace(")", ", 0.08)").replace("rgb", "rgba"),
        hovertemplate=f"%{{x|%a %d %b %H:%M}}<br>{label}: %{{y:.1f}} {unit}<extra></extra>",
    ))
    fig.update_layout(
        margin=dict(t=30, b=10, l=0, r=0),
        height=260,
        xaxis=dict(showgrid=False),
        yaxis=dict(title=unit),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


col_temp, col_humidity, col_wind = st.columns(3)

with col_temp:
    if show_temp or show_feels:
        st.subheader("🌡 Temperature")
        fig = go.Figure()
        if show_temp:
            fig.add_trace(go.Scatter(
                x=df["time"], y=df["temp_c"], name="Temperature",
                line=dict(color="rgb(255,100,80)", width=2),
                hovertemplate="%{x|%a %d %b %H:%M}<br>Temp: %{y:.1f} °C<extra></extra>",
            ))
        if show_feels:
            fig.add_trace(go.Scatter(
                x=df["time"], y=df["feels_like_c"], name="Feels like",
                line=dict(color="rgb(255,180,50)", width=2, dash="dot"),
                hovertemplate="%{x|%a %d %b %H:%M}<br>Feels like: %{y:.1f} °C<extra></extra>",
            ))
        fig.update_layout(
            margin=dict(t=10, b=10, l=0, r=0), height=280,
            xaxis=dict(showgrid=False), yaxis=dict(title="°C"),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig, use_container_width=True)

with col_humidity:
    if show_humidity:
        st.subheader("💧 Humidity")
        st.plotly_chart(
            hourly_line("humidity_pct", "Humidity", "rgb(60,180,180)", "%"),
            use_container_width=True,
        )

with col_wind:
    if show_wind:
        st.subheader("🌬 Wind Speed")
        st.plotly_chart(
            hourly_line("wind_kmh", "Wind", "rgb(140,100,220)", "km/h"),
            use_container_width=True,
        )


# ── Daily summary table ────────────────────────────────────────────────────────
st.divider()
st.subheader("📅 Daily Summary")
display_daily = daily.copy()
display_daily.columns = [
    "Date", "Min °C", "Max °C", "Avg °C",
    "Feels Like °C", "Humidity %", "Precip mm", "Wind Max km/h",
    "Cloud %", "Condition",
]
st.dataframe(display_daily.set_index("Date"), use_container_width=True)

# ── LLM Analysis ───────────────────────────────────────────────────────────────
st.divider()
st.subheader("🤖 LLM Weather Analysis")

if not openai_key:
    st.warning(
        "Add your OpenAI API key in the sidebar to generate a plain-English forecast explanation."
    )
else:
    if st.button("Generate Analysis", type="secondary"):
        os.environ["OPENAI_API_KEY"] = openai_key
        context = build_llm_context(df, daily, label)
        with st.spinner("Asking the LLM to explain the forecast…"):
            try:
                st.session_state.llm_analysis = analyze_weather(context, model=llm_model)
            except Exception as e:
                st.error(f"LLM request failed: {e}")
                st.session_state.llm_analysis = None

    if st.session_state.llm_analysis:
        st.markdown(st.session_state.llm_analysis)
