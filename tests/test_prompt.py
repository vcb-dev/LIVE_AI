from app.prompts.script_block import build_messages
from app.schemas.generate import GenerateScriptBlockRequest, ProductContext


def test_meaning_prompt_requests_fun_fact() -> None:
    messages = build_messages(
        GenerateScriptBlockRequest(
            type="MEANING",
            product=ProductContext(code="SP001", name="Nhẫn kim cương"),
        )
    )

    system = messages[0]["content"]
    user = messages[1]["content"]

    assert "fun fact" in system.lower()
    assert "MEANING" in user
    assert "Fun fact" in user or "fun fact" in user.lower()


def test_meaning_existing_title_asks_for_different_fact() -> None:
    messages = build_messages(
        GenerateScriptBlockRequest(
            type="MEANING",
            product=ProductContext(code="SP001", name="Nhẫn kim cương"),
            existing_title="Fun fact: độ cứng kim cương",
        )
    )

    assert "KHÁC" in messages[1]["content"]
