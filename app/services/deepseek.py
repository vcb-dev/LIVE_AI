import json
import re

from app.config import Settings
from app.schemas.generate import GenerateScriptBlockResponse


class DeepSeekError(Exception):
    pass


def _strip_code_fence(text: str) -> str:
    trimmed = text.strip()
    match = re.match(r"^```(?:json)?\s*(.*?)\s*```$", trimmed, flags=re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else trimmed


def parse_generate_response(raw: str) -> GenerateScriptBlockResponse:
    try:
        payload = json.loads(_strip_code_fence(raw))
        title = str(payload.get("title", "")).strip()
        content = str(payload.get("content", "")).strip()
        duration = int(payload.get("suggestedDurationSec", 60))
        if not title or not content:
            raise ValueError("missing title or content")
        return GenerateScriptBlockResponse(
            title=title[:200],
            content=content[:10000],
            suggested_duration_sec=max(1, min(duration, 3600)),
        )
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        raise DeepSeekError("AI response is not valid JSON") from exc


async def chat_completion(settings: Settings, messages: list[dict[str, str]]) -> str:
    import httpx

    url = f"{settings.deepseek_base_url.rstrip('/')}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.deepseek_api_key}",
        "Content-Type": "application/json",
    }
    body = {
        "model": settings.deepseek_model,
        "messages": messages,
        "temperature": 0.7,
        "response_format": {"type": "json_object"},
    }

    try:
        async with httpx.AsyncClient(timeout=settings.request_timeout_sec) as client:
            response = await client.post(url, headers=headers, json=body)
            response.raise_for_status()
            data = response.json()
            return str(data["choices"][0]["message"]["content"])
    except httpx.HTTPStatusError as exc:
        raise DeepSeekError(f"DeepSeek HTTP {exc.response.status_code}") from exc
    except (httpx.HTTPError, KeyError, IndexError, TypeError) as exc:
        raise DeepSeekError("DeepSeek request failed") from exc


async def generate_script_block(
    settings: Settings,
    messages: list[dict[str, str]],
) -> GenerateScriptBlockResponse:
    raw = await chat_completion(settings, messages)
    try:
        return parse_generate_response(raw)
    except DeepSeekError:
        raise
    except Exception as exc:
        raise DeepSeekError("Failed to parse AI response") from exc
