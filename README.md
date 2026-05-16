# Legal Assistant — Agentic RAG (Capstone)

Educational legal research assistant over **simulated case law and contracts**, built with **LangGraph**, **LangChain**, **FAISS**, and **HuggingFace embeddings** (`BAAI/bge-base-en-v1.5`).

Supports **Gemini**, **OpenAI**, and **DeepSeek** (multi-provider comparison for the capstone).

## Quick start

```powershell
# 1. Clone and enter project
git clone https://github.com/youssefsamirr286/Legal-assistant.git
cd Legal-assistant

# 2. Environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# Edit .env — set at least GEMINI_API_KEY

# 3. Build vector indexes (first run)
.\run_ingest.ps1

# 4. Run UI
.\run_ui.ps1
```

Open **http://localhost:8501**

## Project structure

| Path | Purpose |
|------|---------|
| `src/agent.py` | LangGraph agentic RAG (tools + loop) |
| `src/classic_rag.py` | Classic retrieve-then-generate pipeline |
| `src/ingest.py` | Ingest `data/` → FAISS indexes |
| `src/llm_providers.py` | Gemini / OpenAI / DeepSeek factory |
| `ui_app.py` | Streamlit UI |
| `tests/capstone_scenarios.json` | 10 capstone test queries |
| `tests/evaluate_agent.py` | Faithfulness, latency, cost metrics |
| `MODEL_SELECTION.md` | Model selection analysis (HELM / cost) |
| `data/` | Simulated legal `.txt` corpus |

## Scripts

| Script | Description |
|--------|-------------|
| `run_ui.ps1` | Start Streamlit app |
| `run_ingest.ps1` | Build FAISS indexes |
| `run_evaluation.ps1` | Run 10-scenario evaluation |
| `run_project.ps1` | Setup venv + optional ingest + CLI agent |
| `fix_python_env.ps1` | Repair virtual environment |

## Provider notes

- **Gemini** — recommended default (`LLM_PROVIDER=gemini`).
- **OpenAI** — requires paid API credits (HTTP 429 `insufficient_quota` if empty).
- **DeepSeek** — requires wallet balance (HTTP 402 if empty).
- Set `AUTO_FALLBACK_TO_GEMINI=true` to fall back to Gemini on billing errors.

## Security

- Use **only simulated/public** documents in `data/`.
- Never commit `.env` (API keys). Use `.env.example` as a template.

## License / disclaimer

For **educational use only**. Not legal advice.
