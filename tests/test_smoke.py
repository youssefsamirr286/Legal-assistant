"""Smoke tests for capstone modules (no live LLM calls)."""

import json
from pathlib import Path

from src.agent import app, tools
from src.prompts import get_agent_prompt
from src.retriever import LegalRetriever
from src.security import sanitize_user_input


def test_capstone_scenarios_file_has_ten_cases():
    path = Path(__file__).parent / "capstone_scenarios.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert len(data) == 10
    assert all("query" in row and "name" in row for row in data)


def test_sanitize_strips_and_limits():
    assert sanitize_user_input("  hello  ") == "hello"
    assert len(sanitize_user_input("x" * 5000)) == 4000


def test_retriever_initializes():
    r = LegalRetriever()
    assert r.embeddings is not None or r.init_error is not None


def test_agent_graph_compiles():
    assert app is not None
    assert len(tools) == 3


def test_prompt_template_builds():
    prompt = get_agent_prompt()
    assert "Agentic RAG" in str(prompt)
