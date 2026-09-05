from fastapi import APIRouter, Depends, HTTPException

from app.config import Settings, get_settings
from app.deps import verify_api_key
from app.prompts.script_block import build_messages
from app.schemas.generate import GenerateScriptBlockRequest, GenerateScriptBlockResponse
from app.services.deepseek import DeepSeekError, generate_script_block

router = APIRouter(tags=["generate"], dependencies=[Depends(verify_api_key)])


@router.post("/generate-script-block", response_model=GenerateScriptBlockResponse)
async def generate_script_block_route(
    body: GenerateScriptBlockRequest,
    settings: Settings = Depends(get_settings),
) -> GenerateScriptBlockResponse:
    product_required = body.type in {"PRODUCT_SPEC", "STORY", "MEANING"}
    if product_required and body.product is None:
        raise HTTPException(
            status_code=400,
            detail="Loại block này cần thông tin sản phẩm",
        )

    messages = build_messages(body)
    try:
        return await generate_script_block(settings, messages)
    except DeepSeekError as exc:
        raise HTTPException(status_code=502, detail="Dịch vụ AI tạm thời không phản hồi") from exc
