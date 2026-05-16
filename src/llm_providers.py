"""Multi-provider LLM factory (Gemini, OpenAI, DeepSeek) for the legal agent."""

from __future__ import annotations

import os
from typing import Any, Type

from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool
from langchain_google_genai import ChatGoogleGenerativeAI

try:
    from langchain_openai import ChatOpenAI
except ImportError:  # pragma: no cover - optional until pip install langchain-openai
    ChatOpenAI = None  # type: ignore[assignment,misc]

PLACEHOLDER_KEYS = {
    "your_gemini_api_key_here",
    "your_openai_api_key_here",
    "your_deepseek_api_key_here",
}


def _require_chat_openai() -> Type[Any]:
    if ChatOpenAI is None:
        raise ImportError(
            "langchain-openai is not installed. Run: pip install -r requirements.txt"
        )
    return ChatOpenAI


def _is_valid_key(value: str | None) -> bool:
    return bool(value and value.strip() not in PLACEHOLDER_KEYS)


def get_active_provider() -> str:
    return os.getenv("LLM_PROVIDER", "gemini").strip().lower()


def build_chat_model(provider: str | None = None) -> tuple[BaseChatModel | None, str | None]:
    """Return (chat_model, error_message). Model is not tool-bound."""
    selected = (provider or get_active_provider()).lower()

    if selected == "openai":
        return _build_openai()
    if selected == "deepseek":
        return _build_deepseek()
    if selected == "gemini":
        return _build_gemini()
    return None, f"Unknown LLM_PROVIDER '{selected}'. Use gemini, openai, or deepseek."


def build_llm_with_tools(
    tools: list[BaseTool],
    provider: str | None = None,
) -> tuple[Any | None, str | None]:
    """Return (tool-bound runnable, error_message)."""
    model, error = build_chat_model(provider)
    if model is None:
        return None, error
    return model.bind_tools(tools), None


def _build_gemini() -> tuple[BaseChatModel | None, str | None]:
    api_key = os.getenv("GEMINI_API_KEY")
    if not _is_valid_key(api_key):
        return None, "GEMINI_API_KEY is missing or still a placeholder."

    preferred = os.getenv("GEMINI_MODEL")
    candidates = [m for m in [preferred, "gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"] if m]
    timeout_seconds = int(os.getenv("GEMINI_TIMEOUT_SECONDS", "60"))
    last_error: Exception | None = None

    for model_name in candidates:
        try:
            llm = ChatGoogleGenerativeAI(
                model=model_name,
                temperature=0,
                api_key=api_key,
                timeout=timeout_seconds,
            )
            return llm, None
        except Exception as exc:
            last_error = exc

    return None, f"Could not initialize Gemini. Last error: {last_error}"


def _build_openai() -> tuple[BaseChatModel | None, str | None]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not _is_valid_key(api_key):
        return None, "OPENAI_API_KEY is missing or still a placeholder."

    try:
        openai_cls = _require_chat_openai()
        model_name = os.getenv("OPENAI_MODEL", "gpt-4o")
        llm = openai_cls(model=model_name, temperature=0, api_key=api_key)
        return llm, None
    except Exception as exc:
        return None, f"Could not initialize OpenAI: {exc}"


def _build_deepseek() -> tuple[BaseChatModel | None, str | None]:
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not _is_valid_key(api_key):
        return None, "DEEPSEEK_API_KEY is missing or still a placeholder."

    try:
        openai_cls = _require_chat_openai()
        model_name = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        llm = openai_cls(
            model=model_name,
            temperature=0,
            api_key=api_key,
            base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        )
        return llm, None
    except Exception as exc:
        return None, f"Could not initialize DeepSeek: {exc}"


def provider_display_name(provider: str | None = None) -> str:
    selected = (provider or get_active_provider()).lower()
    names = {
        "gemini": os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        "openai": os.getenv("OPENAI_MODEL", "gpt-4o"),
        "deepseek": os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
    }
    return f"{selected} ({names.get(selected, selected)})"
