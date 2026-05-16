"""Map provider API errors to clear user-facing messages."""

from __future__ import annotations


def is_billing_or_quota_error(exc: BaseException) -> bool:
    text = str(exc).lower()
    markers = (
        "insufficient_quota",
        "insufficient balance",
        "exceeded your current quota",
        "billing",
        "error code: 429",
        "error code: 402",
        "'code': 'insufficient_quota'",
        "'code': 'invalid_request_error'",
    )
    return any(m in text for m in markers)


def format_provider_error(provider: str, exc: BaseException) -> str:
    """Human-readable explanation; not a code bug."""
    text = str(exc).lower()
    name = provider.capitalize()

    if provider == "openai" and (
        "insufficient_quota" in text or ("429" in text and "quota" in text)
    ):
        return (
            f"**{name} — no API credits (HTTP 429)**\n\n"
            "Your key is valid, but the OpenAI account has **no remaining quota**. "
            "This is a **billing** issue, not an app bug.\n\n"
            "**Fix:** Add payment/credits at "
            "[platform.openai.com/account/billing](https://platform.openai.com/account/billing), "
            "or select **Gemini** in the sidebar (recommended for this project)."
        )

    if provider == "deepseek" and ("402" in text or "insufficient balance" in text):
        return (
            f"**{name} — insufficient balance (HTTP 402)**\n\n"
            "Your key is valid, but the DeepSeek wallet needs a **top-up**.\n\n"
            "**Fix:** Add balance at "
            "[platform.deepseek.com](https://platform.deepseek.com/), "
            "or select **Gemini** in the sidebar."
        )

    return (
        f"**{name} request failed**\n\n"
        f"{exc}\n\n"
        "Check your API key, internet connection, and try **Gemini** if another provider fails."
    )


def fallback_notice(failed_provider: str) -> str:
    return (
        f"*Note: {failed_provider.capitalize()} could not bill this request "
        f"(quota/balance). Answering with **Gemini** instead.*\n\n"
    )
