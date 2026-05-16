import json
import os
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

from src.agent import get_agent_response
from src.llm_providers import get_active_provider, provider_display_name
from src.path_setup import ensure_project_cwd

ROOT = ensure_project_cwd()
SCENARIOS_PATH = ROOT / "tests" / "capstone_scenarios.json"
RESULTS_JSON_PATH = ROOT / "tests" / "evaluation_results.json"
REPORT_MD_PATH = ROOT / "tests" / "evaluation_report.md"


def load_scenarios() -> list[dict]:
    with SCENARIOS_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def estimate_cost_usd(text: str, prompt: str, cost_per_1m_input: float = 0.35, cost_per_1m_output: float = 1.05) -> float:
    input_tokens = max(1, int(len(prompt) / 4))
    output_tokens = max(1, int(len(text) / 4))
    in_cost = (input_tokens / 1_000_000) * cost_per_1m_input
    out_cost = (output_tokens / 1_000_000) * cost_per_1m_output
    return round(in_cost + out_cost, 8)


def has_citation_like_output(text: str) -> bool:
    lowered = text.lower()
    citation_hints = ["source:", "[doc", "according to", "retrieved from", "section", "article", "code"]
    return any(h in lowered for h in citation_hints)


def is_successful_response(text: str) -> bool:
    lowered = text.lower()
    failure_hints = ["error:", "failed", "missing", "setup is incomplete", "traceback", "not found"]
    return not any(h in lowered for h in failure_hints)


def evaluate() -> tuple[list[dict], dict]:
    scenarios = load_scenarios()
    rows = []

    for scenario in scenarios:
        query = scenario["query"]
        start = time.perf_counter()
        try:
            answer = get_agent_response(query)
        except Exception as exc:
            answer = f"Error: {exc}"
        latency = round(time.perf_counter() - start, 3)

        success = is_successful_response(answer)
        citations = has_citation_like_output(answer)
        faithfulness_proxy = 1.0 if citations else 0.0
        est_cost = estimate_cost_usd(answer, query)

        rows.append(
            {
                "id": scenario["id"],
                "name": scenario["name"],
                "query": query,
                "latency_seconds": latency,
                "task_success": success,
                "has_citations": citations,
                "faithfulness_proxy": faithfulness_proxy,
                "estimated_cost_usd": est_cost,
                "response_preview": answer[:300].replace("\n", " "),
            }
        )

    summary = {
        "evaluated_at_utc": datetime.now(timezone.utc).isoformat(),
        "llm_provider": get_active_provider(),
        "model": provider_display_name(),
        "total_cases": len(rows),
        "task_success_rate": round(sum(1 for r in rows if r["task_success"]) / max(1, len(rows)), 3),
        "avg_latency_seconds": round(statistics.mean(r["latency_seconds"] for r in rows), 3),
        "p95_latency_seconds": round(sorted(r["latency_seconds"] for r in rows)[max(0, int(len(rows) * 0.95) - 1)], 3),
        "avg_faithfulness_proxy": round(statistics.mean(r["faithfulness_proxy"] for r in rows), 3),
        "total_estimated_cost_usd": round(sum(r["estimated_cost_usd"] for r in rows), 6),
    }
    return rows, summary


def write_outputs(rows: list[dict], summary: dict) -> None:
    with RESULTS_JSON_PATH.open("w", encoding="utf-8") as f:
        json.dump({"summary": summary, "cases": rows}, f, indent=2)

    lines = [
        "# Legal Assistant Evaluation Report",
        "",
        f"- Evaluated at (UTC): `{summary['evaluated_at_utc']}`",
        f"- LLM provider: `{summary['llm_provider']}`",
        f"- Model: `{summary['model']}`",
        f"- Total cases: `{summary['total_cases']}`",
        f"- Task success rate: `{summary['task_success_rate']}`",
        f"- Avg latency (s): `{summary['avg_latency_seconds']}`",
        f"- P95 latency (s): `{summary['p95_latency_seconds']}`",
        f"- Avg faithfulness proxy: `{summary['avg_faithfulness_proxy']}`",
        f"- Total estimated cost (USD): `{summary['total_estimated_cost_usd']}`",
        "",
        "## Case Results",
        "",
    ]

    for row in rows:
        lines.extend(
            [
                f"### {row['id']}. {row['name']}",
                f"- Task success: `{row['task_success']}`",
                f"- Latency (s): `{row['latency_seconds']}`",
                f"- Has citations: `{row['has_citations']}`",
                f"- Faithfulness proxy: `{row['faithfulness_proxy']}`",
                f"- Estimated cost (USD): `{row['estimated_cost_usd']}`",
                f"- Query: {row['query']}",
                f"- Response preview: {row['response_preview']}",
                "",
            ]
        )

    lines.extend(
        [
            "## Notes",
            "",
            "- Faithfulness proxy is heuristic (citation/sourcing signal), not a full judge-model score.",
            "- Cost is estimated from character-based token approximation for capstone reporting.",
        ]
    )

    with REPORT_MD_PATH.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    load_dotenv()
    results, summary = evaluate()
    write_outputs(results, summary)
    print("Evaluation complete.")
    print(f"JSON: {RESULTS_JSON_PATH}")
    print(f"Report: {REPORT_MD_PATH}")
