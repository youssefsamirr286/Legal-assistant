"""Classic RAG pipeline: retrieve from FAISS stores, then generate an answer."""

from __future__ import annotations

import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage

from src.llm_errors import fallback_notice, format_provider_error, is_billing_or_quota_error
from src.llm_providers import build_chat_model, provider_display_name
from src.path_setup import ensure_project_root
from src.retriever import LegalRetriever
from src.security import sanitize_user_input

ensure_project_root()
load_dotenv()

_retriever = LegalRetriever()

CLASSIC_SYSTEM = """You are a legal research assistant using retrieved documents only.
Answer the user's question using ONLY the context below.
Cite sources as [Source: filename].
If context is insufficient, say what is missing.
This is educational research assistance only — not legal advice. Use simulated/public documents only.
"""


def _retrieve_parallel(query: str, k: int = 4) -> str:
    with ThreadPoolExecutor(max_workers=2) as pool:
        contracts_future = pool.submit(_retriever.search_contracts, query, k)
        case_law_future = pool.submit(_retriever.search_case_law, query, k)
        return contracts_future.result() + "\n\n" + case_law_future.result()


def _content_to_str(content: object) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, dict) and block.get("text"):
                parts.append(str(block["text"]))
            else:
                parts.append(str(block))
        return "\n".join(parts)
    return str(content)


def classic_rag_answer(question: str, provider: str | None = None) -> str:
    """Run offline retrieval + online generation (no agent tools)."""
    query = sanitize_user_input(question)
    if not query:
        return "Please enter a legal question."

    context = _retrieve_parallel(query)
    llm, error = build_chat_model(provider)
    if llm is None:
        return f"LLM setup incomplete: {error}"

    selected = (provider or os.getenv("LLM_PROVIDER", "gemini")).lower()
    messages = [
        SystemMessage(content=CLASSIC_SYSTEM),
        HumanMessage(
            content=f"Context:\n{context}\n\nQuestion: {query}\n\nProvide a cited answer."
        ),
    ]
    try:
        response = llm.invoke(messages)
        return _content_to_str(response.content)
    except Exception as exc:
        auto_fallback = os.getenv("AUTO_FALLBACK_TO_GEMINI", "true").lower() in (
            "1",
            "true",
            "yes",
        )
        if auto_fallback and selected != "gemini" and is_billing_or_quota_error(exc):
            gemini_llm, gemini_err = build_chat_model("gemini")
            if gemini_llm is not None:
                try:
                    response = gemini_llm.invoke(messages)
                    return fallback_notice(selected) + _content_to_str(response.content)
                except Exception:
                    pass
        return format_provider_error(selected, exc)


if __name__ == "__main__":
    from src.path_setup import ensure_project_cwd

    ensure_project_cwd()
    sample = "Does COVID-19 qualify as force majeure under a supply contract?"
    print(f"Provider: {provider_display_name()}")
    print(classic_rag_answer(sample))
