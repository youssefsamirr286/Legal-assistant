"""Compare configured LLM providers on one capstone query (latency + preview)."""

import json
import time

from dotenv import load_dotenv

from src.agent import get_agent_response, set_llm_provider
from src.path_setup import ensure_project_cwd

ROOT = ensure_project_cwd()

SAMPLE_QUERY = (
    "Does COVID-19 qualify as force majeure under a supply contract clause "
    "listing natural disasters and governmental action?"
)


def benchmark() -> list[dict]:
    rows = []
    for provider in ("gemini", "openai", "deepseek"):
        ok, err = set_llm_provider(provider)
        if not ok:
            rows.append({"provider": provider, "ok": False, "error": err})
            continue
        start = time.perf_counter()
        try:
            answer = get_agent_response(SAMPLE_QUERY, provider=provider)
            latency = round(time.perf_counter() - start, 3)
            rows.append(
                {
                    "provider": provider,
                    "ok": True,
                    "latency_seconds": latency,
                    "preview": answer[:200].replace("\n", " "),
                }
            )
        except Exception as exc:
            rows.append({"provider": provider, "ok": False, "error": str(exc)})
    return rows


if __name__ == "__main__":
    load_dotenv()
    results = benchmark()
    out_path = ROOT / "tests" / "provider_benchmark.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(json.dumps(results, indent=2))
    print(f"Saved: {out_path}")
