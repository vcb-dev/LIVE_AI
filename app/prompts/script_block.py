import json
from typing import Optional

from app.schemas.generate import BlockType, GenerateScriptBlockRequest, ProductContext

SYSTEM_PROMPT = """\
Bạn là biên kịch livestream bán trang sức Viễn Chí Bảo (Việt Nam).
Viết kịch bản ngắn gọn, tự nhiên, dễ đọc trên sóng live.

Quy tắc theo loại block:
- OPENING / CLOSING / CTA / GAME: title = nhãn ngắn trên màn teleprompter; content = thẻ nhắc việc host cần làm (không văn dài).
- PRODUCT_SPEC: content dùng placeholder {{name}}, {{code}}, {{material}}... nếu thiếu thông tin thì giữ placeholder.
- STORY / MEANING: content là văn nói đọc nguyên văn, cảm xúc, gần gũi.

Luôn trả về JSON thuần (không markdown), đúng schema:
{"title":"...","content":"...","suggestedDurationSec":60}
"""

TYPE_HINTS: dict[BlockType, str] = {
    "OPENING": "Mở đầu buổi live: chào, giới thiệu chủ đề.",
    "PRODUCT_SPEC": "Đọc thông số sản phẩm, có thể dùng placeholder.",
    "STORY": "Câu chuyện gắn với sản phẩm.",
    "MEANING": "Ý nghĩa / thông điệp món trang sức.",
    "CTA": "Kêu gọi hành động: xem SP, inbox, chốt đơn.",
    "GAME": "Trò chơi tương tác: đoán giá, comment may mắn.",
    "CLOSING": "Kết thúc: cảm ơn, hẹn buổi sau.",
}


def _product_lines(product: Optional[ProductContext]) -> str:
    if product is None:
        return "Không có sản phẩm cụ thể."
    attrs = product.attributes or {}
    attrs_text = json.dumps(attrs, ensure_ascii=False) if attrs else "{}"
    return f"Mã: {product.code}\nTên: {product.name}\nThuộc tính: {attrs_text}"


def build_messages(body: GenerateScriptBlockRequest) -> list[dict[str, str]]:
    parts: list[str] = [
        f"Loại block: {body.type}",
        f"Hướng dẫn: {TYPE_HINTS[body.type]}",
        f"Sản phẩm:\n{_product_lines(body.product)}",
    ]
    if body.group_name:
        parts.append(f"Nhóm CTA/trò chơi: {body.group_name}")
    if body.existing_title:
        parts.append(f"Title tham khảo (có thể cải thiện): {body.existing_title}")

    user_prompt = "\n\n".join(parts)
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]
