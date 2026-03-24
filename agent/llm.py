import os
from openai import OpenAI


def get_client() -> OpenAI:
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    if provider == "openrouter":
        return OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def chat(messages: list[dict], model: str | None = None, temperature: float = 0.7) -> str:
    client = get_client()
    resolved_model = model or os.getenv("LLM_MODEL", "gpt-4o-mini")
    response = client.chat.completions.create(
        model=resolved_model,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()
