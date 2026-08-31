from fastapi import Depends, Header, HTTPException

from app.config import Settings, get_settings


async def verify_api_key(
    x_api_key: str = Header(..., alias="X-API-Key"),
    settings: Settings = Depends(get_settings),
) -> None:
    if x_api_key != settings.ai_service_api_key:
        raise HTTPException(status_code=401, detail="API key không hợp lệ")
