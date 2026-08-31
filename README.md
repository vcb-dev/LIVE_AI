# LIVE_AI

Microservice AI cho **LIVE Viễn Chí Bảo** — gọi DeepSeek để gợi ý block kịch bản. Chỉ **LIVE_BE** gọi service này (không public cho FE).

## Cấu trúc

```
app/
  main.py              # FastAPI entry
  config.py            # env settings
  deps.py              # X-API-Key auth
  routes/              # /health, /v1/generate-script-block
  services/deepseek.py # gọi DeepSeek + parse JSON
  schemas/             # request/response DTO
  prompts/             # prompt template theo BlockType
tests/
```

Docker / CI/CD do team deploy cấu hình riêng.

## Yêu cầu

- Python 3.9+

## Chạy local

```bash
cd LIVE_AI
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

cp .env.example .env
# Sửa DEEPSEEK_API_KEY và AI_SERVICE_API_KEY

uvicorn app.main:app --reload --port 8000
```

- Health: `GET http://localhost:8000/health`
- Generate: `POST http://localhost:8000/v1/generate-script-block`
  - Header: `X-API-Key: <AI_SERVICE_API_KEY>`

## Env

| Biến | Bắt buộc | Mô tả |
|------|----------|--------|
| `DEEPSEEK_API_KEY` | ✅ | Key DeepSeek — **chỉ lưu ở repo AI** |
| `AI_SERVICE_API_KEY` | ✅ | Shared secret với LIVE_BE |
| `DEEPSEEK_BASE_URL` | | Mặc định `https://api.deepseek.com` |
| `DEEPSEEK_MODEL` | | Mặc định `deepseek-chat` |
| `REQUEST_TIMEOUT_SEC` | | Mặc định `60` |

Trên **LIVE_BE** (không commit key DeepSeek):

```bash
AI_SERVICE_URL=http://localhost:8000
AI_SERVICE_API_KEY=<cùng giá trị AI_SERVICE_API_KEY>
```

## Test

```bash
pytest
ruff check app tests
```

## API v1

### `POST /v1/generate-script-block`

**Request**

```json
{
  "type": "STORY",
  "product": {
    "code": "SP001",
    "name": "Nhẫn kim cương",
    "attributes": { "material": "Vàng 18K" }
  },
  "group_name": null,
  "existing_title": null,
  "locale": "vi"
}
```

**Response**

```json
{
  "title": "Nhẫn kim cương — câu chuyện tình yêu",
  "content": "...",
  "suggested_duration_sec": 60
}
```

`STORY`, `MEANING`, `PRODUCT_SPEC` bắt buộc có `product`.
