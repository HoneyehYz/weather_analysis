import os
from openai import OpenAI

SYSTEM_PROMPT = (
    "You are a friendly meteorologist assistant. "
    "Given a structured weather data summary, explain the upcoming 7-day forecast "
    "in plain English — no jargon. Mention notable patterns such as temperature swings, "
    "rain events, or unusually warm/cold stretches. Keep it to 3–4 short paragraphs."
)


def analyze_weather(context: str, model: str | None = None) -> str:
    """Send the weather summary to the LLM and return its explanation."""
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    resolved_model = model or os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

    response = client.chat.completions.create(
        model=resolved_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": context},
        ],
        temperature=0.5,
        max_tokens=500,
    )
    return response.choices[0].message.content.strip()
