# N8N & OpenAI Agent Builder (Capstone Optional Paths)

This project implements the **code path** (LangGraph + LangChain). The same pipeline can be mirrored in no-code tools:

## N8N workflow (self-hosted)

1. **Webhook** — receives `question` JSON from a form or chat UI.
2. **HTTP Request** — `POST` to your Streamlit backend or a small FastAPI wrapper calling `get_agent_response(question)`.
3. **IF** — branch on whether response contains `Error` or `setup is incomplete`.
4. **Email / Slack** — notify reviewer when evaluation metrics fail thresholds.

Equivalent nodes map to: ingest (scheduled), retrieval (HTTP to `/classic-rag`), agent (HTTP to `/agent`), evaluation (scheduled run of `tests/evaluate_agent.py`).

## OpenAI Agent Builder / Assistants

- Upload the same simulated `.txt` corpus from `data/` as assistant files.
- Enable **File Search** for contract + case law bundles.
- System instructions: copy from `src/prompts.py` (`SYSTEM_PROMPT`).
- Compare answers to this repo’s LangGraph agent using the 10 queries in `tests/capstone_scenarios.json`.

## Security reminder

Use **simulated documents only**. Never upload real client files to cloud assistants.
