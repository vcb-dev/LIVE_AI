import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.services import deepseek as deepseek_service


@pytest.mark.asyncio
async def test_generate_requires_api_key() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/v1/generate-script-block",
            json={
                "type": "OPENING",
            },
        )

    assert response.status_code == 422 or response.status_code == 401


@pytest.mark.asyncio
async def test_generate_story_success(api_key: str, monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_generate(settings, messages):  # noqa: ARG001
        return deepseek_service.parse_generate_response(
            '{"title":"Chuyện nhẫn","content":"Ngày xưa...","suggestedDurationSec":45}'
        )

    monkeypatch.setattr("app.routes.generate.generate_script_block", fake_generate)

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/v1/generate-script-block",
            headers={"X-API-Key": api_key},
            json={
                "type": "STORY",
                "product": {
                    "code": "SP001",
                    "name": "Nhẫn kim cương",
                    "attributes": {"material": "Vàng 18K"},
                },
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Chuyện nhẫn"
    assert data["content"] == "Ngày xưa..."
    assert data["suggested_duration_sec"] == 45


@pytest.mark.asyncio
async def test_generate_product_block_requires_product(api_key: str) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/v1/generate-script-block",
            headers={"X-API-Key": api_key},
            json={"type": "STORY"},
        )

    assert response.status_code == 400


def test_parse_generate_response_strips_markdown_fence() -> None:
    raw = '```json\n{"title":"A","content":"B","suggestedDurationSec":30}\n```'
    parsed = deepseek_service.parse_generate_response(raw)
    assert parsed.title == "A"
    assert parsed.content == "B"
    assert parsed.suggested_duration_sec == 30
