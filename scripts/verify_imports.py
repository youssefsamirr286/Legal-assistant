"""Verify all third-party imports used by the project (run after pip install)."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

PACKAGES = [
    "langchain",
    "langchain_core",
    "langchain_community",
    "langchain_text_splitters",
    "langchain_google_genai",
    "langchain_openai",
    "langchain_huggingface",
    "langgraph",
    "faiss",
    "tiktoken",
    "dotenv",
    "streamlit",
    "sentence_transformers",
    "numpy",
    "fitz",  # pymupdf
    "pytest",
]

MODULES = [
    "src.agent",
    "src.classic_rag",
    "src.ingest",
    "src.retriever",
    "src.prompts",
    "src.llm_providers",
    "src.security",
]


def main() -> int:
    failed: list[str] = []
    for name in PACKAGES:
        try:
            importlib.import_module(name)
            print(f"OK  {name}")
        except ImportError as exc:
            print(f"FAIL {name}: {exc}")
            failed.append(name)

    for name in MODULES:
        try:
            importlib.import_module(name)
            print(f"OK  {name}")
        except ImportError as exc:
            print(f"FAIL {name}: {exc}")
            failed.append(name)

    if failed:
        print(f"\n{len(failed)} import(s) failed.")
        return 1
    print("\nAll imports verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
