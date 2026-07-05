"""Run the example queries and generate examples/example_runs.md.

Two modes:
  - full: When an LLM key is present, run_agent() drives the real agent through
    tool orchestration (the actual production path).
  - scripted: When no key is present, a human replays the tool-call sequence the
    agent would pick. The search, aggregation, and assembly all run through the
    real code (real CT.gov API); only tool selection/order is chosen by a human.
    The generation mode is disclosed inside example_runs.md.

Usage:
  PYTHONPATH=. uv run python scripts/run_examples.py
"""

import json
from pathlib import Path

from app.agent.runner import assemble_response, run_agent
from app.agent.session import Session
from app.agent.tools import make_tools
from app.config import settings

# Each example: (description, request payload, function that plays the expected tool sequence).
# The sequence function receives the tools dict produced by make_tools and invokes them in order.


def seq_time_trend(t):
    t["analyze_time_trend"].invoke(
        {
            "title": "Pembrolizumab trials over time (since 2015)",
            "drug_name": "Pembrolizumab",
            "start_year": 2015,
        }
    )


def seq_distribution(t):
    t["analyze_distribution"].invoke(
        {"field": "phase", "title": "Diabetes trials by phase", "condition": "diabetes"}
    )


def seq_comparison(t):
    t["analyze_comparison"].invoke(
        {
            "filter_sets": [
                {"label": "pembro", "drug_name": "Pembrolizumab"},
                {"label": "nivo", "drug_name": "Nivolumab"},
            ],
            "title": "Pembrolizumab vs Nivolumab by phase",
            "field": "phase",
        }
    )


def seq_geo(t):
    t["analyze_distribution"].invoke(
        {
            "field": "country",
            "title": "Recruiting breast cancer trials by country",
            "condition": "breast cancer",
            "overall_status": "RECRUITING",
        }
    )


def seq_network(t):
    t["analyze_network"].invoke(
        {
            "dimension": "sponsor_drug",
            "title": "Sponsor–drug network for melanoma",
            "condition": "melanoma",
        }
    )


def seq_empty(t):
    # Zero results → the tool exits without committing → no_data response.
    t["analyze_distribution"].invoke(
        {"field": "phase", "title": "(no results expected)", "drug_name": "Zzzznonexistentdrug"}
    )


EXAMPLES = [
    ("Time trend — trial count per year for a specific drug", {"query": "How has the number of Pembrolizumab trials changed per year since 2015?"}, seq_time_trend),
    ("Distribution — a condition's distribution by phase", {"query": "How are diabetes trials distributed across phases?", "condition": "diabetes"}, seq_distribution),
    ("Comparison — two drugs compared by phase", {"query": "Compare trial phases for Pembrolizumab vs Nivolumab."}, seq_comparison),
    ("Geographic — recruiting trial counts by country", {"query": "Which countries have the most recruiting trials for breast cancer?", "condition": "breast cancer"}, seq_geo),
    ("Network — sponsor↔drug relationships for a condition", {"query": "Show a network of sponsors and drugs for melanoma trials.", "condition": "melanoma"}, seq_network),
    ("Empty result — a nonexistent drug (graceful handling)", {"query": "How are trials for Zzzznonexistentdrug distributed across phases?"}, seq_empty),
]


def run_scripted(payload: dict, seq) -> dict:
    session = Session(input_filters={k: v for k, v in payload.items() if k != "query"})
    tools = {t.name: t for t in make_tools(session)}
    seq(tools)
    return assemble_response(session)


def main() -> None:
    has_key = bool(settings.anthropic_api_key or settings.openai_api_key)
    mode = (
        "full (the real ReAct agent orchestrates tools)"
        if has_key
        else "scripted (tool sequence replayed; data and aggregation come from real API/code)"
    )

    lines = [
        "# Example Runs",
        "",
        f"> Generation mode: **{mode}**",
        "> Every `data` / `citations` value is aggregated from the real ClinicalTrials.gov v2 API response by the deterministic tools.",
        "> In `scripted` mode a human only replays the **order of tool calls** the agent would pick at runtime;"
        " the actual search, aggregation, and assembly all run through the real code (numbers never pass through the LLM).",
        "",
    ]

    for title, payload, seq in EXAMPLES:
        print(f"running: {title}")
        try:
            result = run_agent(payload["query"], {k: v for k, v in payload.items() if k != "query"}) if has_key else run_scripted(payload, seq)
        except Exception as e:  # noqa: BLE001
            result = {"error": f"{type(e).__name__}: {e}"}

        lines += [
            f"## {title}", "",
            "**Request:**", "```json", json.dumps(payload, ensure_ascii=False, indent=2), "```", "",
            "**Response:**", "```json", json.dumps(result, ensure_ascii=False, indent=2), "```", "",
        ]

    out = Path(__file__).parent.parent / "examples" / "example_runs.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
