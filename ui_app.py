import json
import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from src.path_setup import ensure_project_root

ensure_project_root()

from src.agent import get_agent_response, set_llm_provider
from src.classic_rag import classic_rag_answer
from src.llm_providers import get_active_provider, provider_display_name
from src.security import sanitize_user_input

load_dotenv()

SCENARIOS_PATH = Path("tests/capstone_scenarios.json")


@st.cache_data
def load_capstone_scenarios() -> list[dict]:
    if SCENARIOS_PATH.exists():
        with SCENARIOS_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    return []


def _provider_ready(provider: str) -> bool:
    keys = {
        "gemini": "GEMINI_API_KEY",
        "openai": "OPENAI_API_KEY",
        "deepseek": "DEEPSEEK_API_KEY",
    }
    env_name = keys.get(provider, "")
    value = os.getenv(env_name, "")
    return bool(value) and "your_" not in value


st.set_page_config(page_title="Legal Assistant - Agentic RAG", page_icon="⚖", layout="wide")

st.title("⚖ Legal Assistant Powered by Agentic RAG")
st.caption(
    "Educational use only — simulated/public legal documents. "
    "Not legal advice; consult a licensed attorney."
)

scenarios = load_capstone_scenarios()

with st.sidebar:
    st.header("Configuration")
    provider = st.selectbox(
        "LLM Provider",
        options=["gemini", "openai", "deepseek"],
        index=["gemini", "openai", "deepseek"].index(get_active_provider())
        if get_active_provider() in {"gemini", "openai", "deepseek"}
        else 0,
    )
    if provider != get_active_provider():
        ok, err = set_llm_provider(provider)
        if not ok and err:
            st.warning(err)

    if provider == "openai":
        st.info(
            "OpenAI needs **paid credits** on your account. "
            "HTTP 429 `insufficient_quota` means billing, not a broken key."
        )
    elif provider == "deepseek":
        st.info(
            "DeepSeek needs a **positive wallet balance**. "
            "HTTP 402 means top up at platform.deepseek.com."
        )
    else:
        st.success("Gemini is the recommended provider for this capstone (free tier).")

    pipeline_mode = st.radio(
        "Pipeline",
        options=["Agentic RAG (LangGraph)", "Classic RAG"],
        index=0,
    )

    st.header("System Status")
    st.write(f"Active provider: `{provider_display_name(provider)}`")
    st.write(f"API key: {'✅' if _provider_ready(provider) else '❌'}")
    st.write(f"Contracts index: {'✅' if Path('faiss_index/contracts').exists() else '❌'}")
    st.write(f"Case law index: {'✅' if Path('faiss_index/case_law').exists() else '❌'}")

    if not Path("faiss_index/contracts").exists() or not Path("faiss_index/case_law").exists():
        st.info("Run `python src/ingest.py` or `.\\run_ingest.ps1` to build FAISS indexes.")

    st.markdown("---")
    st.subheader("Capstone Scenarios (10)")
    for scenario in scenarios:
        label = f"{scenario['id']}. {scenario['name']}"
        if st.button(label, use_container_width=True, key=f"scenario_{scenario['id']}"):
            st.session_state["prefill_prompt"] = scenario["query"]

if "messages" not in st.session_state:
    st.session_state["messages"] = []


def run_pipeline(prompt: str) -> str:
    safe = sanitize_user_input(prompt)
    if pipeline_mode.startswith("Classic"):
        return classic_rag_answer(safe, provider=provider)
    return get_agent_response(safe, provider=provider)


if st.session_state.get("prefill_prompt"):
    prefill = st.session_state["prefill_prompt"]
    if not st.session_state["messages"] or st.session_state["messages"][-1]["role"] != "user":
        st.session_state["messages"].append({"role": "user", "content": prefill})
        with st.spinner("Analyzing legal question..."):
            answer = run_pipeline(prefill)
        st.session_state["messages"].append({"role": "assistant", "content": answer})
        st.session_state["prefill_prompt"] = ""

for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_prompt = st.chat_input("Ask a legal question...")
if user_prompt:
    st.session_state["messages"].append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    with st.chat_message("assistant"):
        with st.spinner("Researching case law and contracts..."):
            answer = run_pipeline(user_prompt)
        st.markdown(answer)

    st.session_state["messages"].append({"role": "assistant", "content": answer})
