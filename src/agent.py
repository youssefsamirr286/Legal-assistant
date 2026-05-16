from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Annotated, Any, Literal, Sequence, TypedDict

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.tools import tool
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from src.llm_errors import (
    fallback_notice,
    format_provider_error,
    is_billing_or_quota_error,
)
from src.llm_providers import build_llm_with_tools, get_active_provider, provider_display_name
from src.path_setup import ensure_project_cwd, ensure_project_root
from src.prompts import get_agent_prompt
from src.retriever import LegalRetriever
from src.security import sanitize_user_input

ensure_project_root()
load_dotenv()

retriever = LegalRetriever()
MAX_AGENT_ITERATIONS = int(os.getenv("AGENT_MAX_ITERATIONS", "6"))
AUTO_FALLBACK_TO_GEMINI = os.getenv("AUTO_FALLBACK_TO_GEMINI", "true").lower() in (
    "1",
    "true",
    "yes",
)

_current_provider = get_active_provider()


@tool
def search_contracts(query: str) -> str:
    """Search the contracts database for relevant clauses, employment agreements, NDAs, and SaaS subscriptions."""
    return retriever.search_contracts(query)


@tool
def search_case_law(query: str) -> str:
    """Search the case law database for legal precedents, statutes, and court decisions."""
    return retriever.search_case_law(query)


@tool
def search_all_legal_sources(query: str) -> str:
    """Search case law AND contracts in parallel. Use for complex questions spanning both corpora."""
    return retriever.search_all_parallel(query)


tools = [search_contracts, search_case_law, search_all_legal_sources]

llm_with_tools, llm_init_error = build_llm_with_tools(tools, _current_provider)


def set_llm_provider(provider: str) -> tuple[bool, str | None]:
    """Switch LLM provider at runtime (gemini | openai | deepseek)."""
    global llm_with_tools, llm_init_error, _current_provider
    os.environ["LLM_PROVIDER"] = provider.strip().lower()
    _current_provider = os.environ["LLM_PROVIDER"]
    llm_with_tools, llm_init_error = build_llm_with_tools(tools, _current_provider)
    return llm_with_tools is not None, llm_init_error


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    iteration_count: int


def agent_node(state: AgentState):
    iteration = state.get("iteration_count", 0)
    if llm_with_tools is None:
        return {
            "messages": [
                AIMessage(
                    content=(
                        f"LLM setup is incomplete for provider '{_current_provider}'. "
                        f"{llm_init_error or 'Configure API keys in .env and restart.'}"
                    )
                )
            ],
            "iteration_count": iteration + 1,
        }

    prompt = get_agent_prompt()
    chain = prompt | llm_with_tools
    try:
        response = chain.invoke({"messages": state["messages"]})
        return {"messages": [response], "iteration_count": iteration + 1}
    except KeyboardInterrupt:
        return {
            "messages": [AIMessage(content="Request cancelled by user.")],
            "iteration_count": iteration + 1,
        }
    except Exception as exc:
        if (
            AUTO_FALLBACK_TO_GEMINI
            and _current_provider != "gemini"
            and is_billing_or_quota_error(exc)
        ):
            fallback_llm, _ = build_llm_with_tools(tools, "gemini")
            if fallback_llm is not None:
                try:
                    response = (prompt | fallback_llm).invoke({"messages": state["messages"]})
                    prefix = fallback_notice(_current_provider)
                    body = _message_content_to_str(response.content)
                    return {
                        "messages": [AIMessage(content=prefix + body)],
                        "iteration_count": iteration + 1,
                    }
                except Exception:
                    pass

        return {
            "messages": [
                AIMessage(content=format_provider_error(_current_provider, exc))
            ],
            "iteration_count": iteration + 1,
        }


def should_continue(state: AgentState) -> Literal["continue", "end"]:
    if state.get("iteration_count", 0) >= MAX_AGENT_ITERATIONS:
        return "end"
    last_message = state["messages"][-1]
    tool_calls = getattr(last_message, "tool_calls", None) or []
    if tool_calls:
        return "continue"
    return "end"


workflow = StateGraph(AgentState)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", ToolNode(tools))
workflow.add_edge(START, "agent")
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {"continue": "tools", "end": END},
)
workflow.add_edge("tools", "agent")

app = workflow.compile()


def _message_content_to_str(content: Any) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("text"):
                parts.append(str(block["text"]))
            else:
                parts.append(str(block))
        return "\n".join(parts)
    return str(content)


def get_agent_response(question: str, provider: str | None = None) -> str:
    """Return the final assistant response for a single sanitized question."""
    if provider and provider.lower() != _current_provider:
        set_llm_provider(provider)

    safe_question = sanitize_user_input(question)
    if not safe_question:
        return "Please enter a legal question."

    state: AgentState = {
        "messages": [HumanMessage(content=safe_question)],
        "iteration_count": 0,
    }
    final_content = ""
    for event in app.stream(state):
        for value in event.values():
            if "messages" in value:
                last_message = value["messages"][-1]
                if not getattr(last_message, "tool_calls", None):
                    final_content = _message_content_to_str(last_message.content)

    if not final_content:
        final_content = "No response generated. Please try again."
    return final_content


def query_agent(question: str):
    try:
        print("Assistant:", get_agent_response(question))
    except KeyboardInterrupt:
        print("Assistant: Request cancelled.")
    except Exception as exc:
        print(f"Assistant: Something went wrong: {exc}")


if __name__ == "__main__":
    ensure_project_cwd()

    print("Legal Agent (LangGraph) — Agentic RAG")
    print(f"Provider: {provider_display_name(_current_provider)}")
    if llm_with_tools is None:
        print(f"Startup warning: {llm_init_error}")
    print("Type your legal question (or 'exit' to quit):")
    while True:
        try:
            q = input("> ")
        except (EOFError, KeyboardInterrupt):
            print("\nExiting agent.")
            break
        if q.lower() in ["exit", "quit"]:
            break
        query_agent(q)
