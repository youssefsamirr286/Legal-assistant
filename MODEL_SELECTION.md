# Model Selection Analysis — Legal Assistant Capstone

## 1) Candidate Models

- **Primary (implemented):** Google Gemini 2.5 Flash (`gemini-2.5-flash`)
- **Alternative 1:** OpenAI GPT-4o (`gpt-4o`)
- **Alternative 2:** DeepSeek Chat (`deepseek-chat`)

## 2) HELM Evidence (LegalBench and related tasks)

- **Source:** [HELM](https://crfm.stanford.edu/helm/)
- **Scenarios compared:** LegalBench, BoolQ (enforceability yes/no), NarrativeQA (long contract reading)
- **Observed pattern (public leaderboard snapshots):** GPT-4o and Gemini 1.5 Pro rank highly on legal reasoning and long-context tasks; Mistral-Large is competitive on cost.
- **Key takeaway:** For **citation-grounded RAG** (not open-book bar exam), instruction-following + tool use matter as much as LegalBench exact match. Gemini Flash offers strong quality at lower cost for iterative agent loops.

## 3) Artificial Analysis Evidence (cost / speed / latency)

| Factor | Target (spec) | Gemini 2.5 Flash | GPT-4o | DeepSeek Chat |
|--------|---------------|------------------|--------|---------------|
| Quality index | > 70 | ~75+ tier | ~85+ tier | ~78 tier |
| Output speed | > 50 tok/s | High | Medium | High |
| Context window | > 32K | 1M class | 128K | 64K+ |
| Input cost | < $10/M | Low | Higher | Very low |
| TTFT | < 2s | Good | Good | Good |

- **Source:** [Artificial Analysis](https://artificialanalysis.ai/)
- **Key takeaway:** **Gemini Flash** selected for default capstone runs (cost + speed for multi-step agent). **GPT-4o** best when highest instruction fidelity is required. **DeepSeek** best cost alternative for benchmarking.

## 4) LLM Arena Evidence (human preference)

- **Source:** [LLM Arena](https://lmarena.ai/)
- **Observation:** GPT-4o and Claude families lead instruction-following; Gemini competitive on hard prompts and long documents.
- **Key takeaway:** Legal prompts are multi-step and citation-heavy — align with Arena “hard prompts” / instruction-following leaders; validate with project scenarios in `tests/capstone_scenarios.json`.

## 5) Decision Matrix (weighted)

| Criterion | Weight | Gemini Flash | GPT-4o | DeepSeek |
|-----------|--------|--------------|--------|----------|
| Legal prompt reliability | 30% | 8 | 9 | 8 |
| Latency (agent loops) | 25% | 9 | 7 | 8 |
| Cost | 25% | 9 | 5 | 9 |
| Long contract context | 20% | 9 | 8 | 7 |
| **Weighted score** | | **8.65** | **7.35** | **8.05** |

## 6) Final Selection

- **Selected model:** `gemini-2.5-flash` via `LLM_PROVIDER=gemini`
- **Why:** Best balance for Agentic RAG (multiple tool calls per question), low cost for evaluation runs, sufficient quality on simulated corpus.
- **Limitations:** Occasional verbose outputs; block-style content needs normalization (handled in `src/agent.py`).
- **Mitigations:** RAG grounding, faithfulness proxy in evaluation, mandatory citations in system prompt, human review disclaimer.

## 7) Project Configuration

Set in `.env` (see `.env.example`):

```env
LLM_PROVIDER=gemini
GEMINI_MODEL=gemini-2.5-flash
```

Switch providers in Streamlit sidebar or:

```powershell
$env:LLM_PROVIDER="openai"
python tests/benchmark_providers.py
```
