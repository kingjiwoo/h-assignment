# ClinicalTrials.gov Query-to-Visualization Agent (Backend)

A backend service that takes a natural-language clinical-trial question, queries and aggregates real data from the [ClinicalTrials.gov v2 API](https://clinicaltrials.gov/data-api/api), and returns a **structured visualization spec (JSON)** the frontend can render as-is.

- **Stack:** Python 3.11+, FastAPI, LangGraph (`create_react_agent`), Pydantic
- **Agent shape:** A ReAct agent where the LLM orchestrates tools. Crucially, **every number is computed by deterministic tools** — the LLM never fabricates values.
- **Supported visualizations:** `time_series`, `bar_chart`, `grouped_bar_chart`, `network_graph` (plus `no_data` for empty results)
- **Supported question types:** time trends · distributions · comparisons · geographic distributions · relationship graphs
- **Bonus:** Deep Citations that attach the source `nct_id` and an actual API text excerpt to each data point.

---

## 1. Quickstart (Run)

### 1-A. One-shot with Docker Compose (recommended)

Boots both the backend (FastAPI on :8000) and frontend (Next.js on :3000) in a single command. You don't need Python or Node on the host.

```bash
cp .env.example .env          # Fill in either ANTHROPIC_API_KEY or OPENAI_API_KEY
docker compose up --build     # First build takes ~1–2 min; cached afterwards
# → http://localhost:3000 (frontend),  http://localhost:8000/docs (Swagger)
```

- Hot reload: `app/` and `frontend/src/` are volume-mounted into the containers, and `uvicorn --reload` / `next dev` pick up changes.
- The frontend only starts after the backend's `/health` succeeds (`depends_on: service_healthy`).
- `node_modules` lives in a named volume, so it never leaks into the host `frontend/node_modules`.

Shut down with `Ctrl+C`; remove containers with `docker compose down` (add `-v` to also drop volumes).

### 1-B. Local, no Docker

```bash
uv sync                       # or: pip install -e .
cp .env.example .env
uv run uvicorn app.main:app --reload            # backend on :8000
# In another terminal
cd frontend && pnpm install && pnpm dev         # frontend on :3000 → calls backend :8000
```

### Environment variables

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | one of the two | For Anthropic |
| `OPENAI_API_KEY` | one of the two | For OpenAI |
| `LLM_PROVIDER` | optional | `anthropic`\|`openai` (auto-selected from whichever key is present, Anthropic first) |
| `LLM_MODEL` | optional | Model name override |
| `MAX_STUDIES` | optional | Per-request cap on studies pulled from CT.gov (default 500) |

### Example call
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Show a network of sponsors and drugs for melanoma trials.", "condition": "melanoma"}'
```

### Tests / regenerating examples
```bash
uv run pytest                                        # Unit + integration tests for aggregation/tools/assembly (no network / no LLM needed)
PYTHONPATH=. uv run python scripts/run_examples.py   # Regenerates examples/example_runs.md
```

See [`frontend/README.md`](./frontend/README.md) for frontend-specific details.

---

## 2. Request schema

`POST /query`, `Content-Type: application/json`. Only `query` is required; the rest are optional filters.
**Explicitly supplied filters always beat values the agent infers from natural language** (deterministically merged in the tool layer).

| Field | Type | Required | Description / validation |
|---|---|---|---|
| `query` | string | ✅ | Natural-language question (min length 1) |
| `drug_name` | string | ❌ | Intervention/drug name, e.g., `Pembrolizumab` |
| `condition` | string | ❌ | Condition, e.g., `breast cancer` |
| `sponsor` | string | ❌ | Sponsor name |
| `country` | string | ❌ | Country, e.g., `Canada` |
| `trial_phase` | string | ❌ | `EARLY_PHASE1`\|`PHASE1`\|`PHASE2`\|`PHASE3`\|`PHASE4`\|`NA` |
| `start_year` | int | ❌ | Start year (inclusive) |
| `end_year` | int | ❌ | End year (inclusive) |

Pydantic (`app/schemas.py`) validates types/required fields; violations return HTTP 422.

---

## 3. Response schema

```jsonc
{
  "visualization": {
    "type": "network_graph",       // time_series | bar_chart | grouped_bar_chart | network_graph | no_data
    "title": "Human-readable title",
    "encoding": { ... },            // See the per-type table below
    "data": [ ... ] | { ... }       // See the per-type table below
  },
  "meta": {
    "filters": { ... },             // Echoes the filters supplied on the request
    "analysis_type": "network",     // time_trend|distribution|comparison|geo|network|null
    "source": "clinicaltrials.gov",
    "study_count": 300,             // Number of studies used for aggregation
    "capped": true,                // Whether MAX_STUDIES was hit
    "notes": [ "..." ]              // Human-readable notes on assumptions/filters/truncation
  },
  "citations": {                    // (Bonus) null if absent
    "<bucket_key>": [ { "nct_id": "NCT...", "excerpt": "Verbatim excerpt from the API response" } ]
  }
}
```

### `encoding` / `data` shape per chart type

| type | encoding | data |
|---|---|---|
| `time_series` | `{x:{field:"year",type:"temporal"}, y:{field:"trial_count",type:"quantitative"}}` | `[{year, trial_count}]` |
| `bar_chart` (distribution) | `{x:{field:"category"}, y:{field:"trial_count"}}` | `[{category, trial_count}]` |
| `bar_chart` (geo) | `{x:{field:"country"}, y:{field:"trial_count"}}` | `[{country, trial_count}]` |
| `grouped_bar_chart` | `{x:{field:"category"}, y:{field:"<group>"}, series:[labels...]}` | `[{category, "<label1>":n, "<label2>":n}]` |
| `network_graph` | `{nodes:{id,group,size}, edges:{source,target,weight}}` | `{nodes:[{id,kind,degree}], edges:[{source,target,weight}]}` |
| `no_data` | `{}` | `[]` |

### Citations `bucket_key` conventions
- Distribution / time / geo: the data point's category value (e.g., `"PHASE3"`, `"2020"`, `"Canada"`)
- Comparison: `"<group_label>|<category>"` (e.g., `"nivo|PHASE2"`)
- Network: `"<source>|<target>"` (e.g., `"Merck Sharp & Dohme LLC|Pembrolizumab"`)

Capped at 3 citations per bucket.

---

## 4. Architecture & design decisions

### Shape: a "constrained ReAct agent"

The LLM **orchestrates** tools (deciding what to search and which aggregation to combine), but **every number is computed by deterministic tools**. See [`docs/architecture.md`](docs/architecture.md) for a diagram.

```
POST /query
   │
   ▼
create_react_agent (LLM)  ──▶ Tool-call loop (LLM decides order and combinations)
   │
   ├─ analyze_time_trend(filters, title)          : CT.gov search + yearly aggregation → time_series
   ├─ analyze_distribution(field, filters, title) : phase/intervention_type/status/country distribution → bar_chart
   ├─ analyze_comparison(filter_sets, field)      : parallel searches compared on a shared axis → grouped_bar_chart
   ├─ analyze_network(dimension, filters)         : sponsor↔drug / drug↔drug relationship graph → network_graph
   └─ report_unresolvable(reason, missing)        : honest abstention when the target cannot be pinned down
   │
   ▼
The server assembles the QueryResponse straight from the Session's artifact (the real data the tool computed)
```

**Core safeguard — numbers never pass through the LLM:**
Tools compute the actual figures via `app/core` (the aggregation core) and **store them on the Session**; the LLM only sees a summary (preview). The final response is assembled by the **server pulling from Session artifacts directly** — not from LLM-written text. Structurally, there is no path for the LLM to invent a trial count or make a transcription error.

### Layer layout
| Layer | Location | Responsibility |
|---|---|---|
| API | `app/main.py` | FastAPI, request validation, explicit-filter extraction |
| Orchestration | `app/agent/` | `runner` (agent execution + response assembly), `tools` (tools), `session` (per-request state) |
| Compute core | `app/core/` | `aggregate` (5 pure aggregations), `extractors` (field extraction), `query` (params builder) — **LLM-independent, fully unit-tested** |
| External integrations | `app/services/` | `ctgov_client` (CT.gov HTTP), `llm` (provider-agnostic) |

### Key decisions and tradeoffs

**1) Why a ReAct agent (`create_react_agent`) — extensibility**
Hard-coding question types in the code (fixed switch) would require code changes for every new question class, hurting extensibility. Letting the agent **compose tools at runtime** means new combinations (a certain filter + a certain aggregation) — and even multi-step questions in the future ("find the top sponsors → look at their trends") — can be supported **without code changes**.

**2) But number-generation is never delegated — hallucination guard**
The core risk of ReAct is the LLM inventing numbers. So every count/aggregation is walled off in pure functions under `app/core` (invoked by tools), and the LLM only handles "judgment" (tool choice, filter extraction, title generation). Tool-computed values are stored on the Session and reach the response bypassing LLM text. → Directly addresses the rubric's "avoid hallucination-prone steps / validation·constraints."

**3) Deterministic core reuse — testability**
The 5 aggregation functions are essentially "generic group-by-count + a network special case." Keeping them as pure functions under `app/core`, separate from orchestration (the agent), makes them fully unit-testable from fixtures alone — no network, no LLM. Swapping the orchestration from graph to agent left this core and its tests untouched.

**4) Deliberately no entity-name normalization layer**
CT.gov's search engine (Essie) already handles brand names (`Keytruda` → Pembrolizumab), typos (`pembrolizumb`), and synonyms (`heart attack`) — confirmed empirically. A separate normalization tool would be over-engineering.

**5) Sensible handling of real API data — cap & top-N**
Since there is no server-side group-by, we pull studies within the filter range and aggregate in memory, but cap at `MAX_STUDIES` and mark `meta.capped=true` plus a note when the cap is hit ("sample-based"). Networks keep the top 60 edges and geo keeps the top 25 countries; the truncation is disclosed in the notes so what we return is a hub-focused, meaningful relationship graph.

### Extension points
- **Add an aggregation axis:** Extend the `field` set in the analyze tools and add a mapping in `app/core/aggregate`. Tool signatures stay stable → the agent picks it up automatically.
- **Add a tool:** Drop a new `@tool` into `app/agent/tools.py`. The agent can start composing it via the prompt alone.

---

## 5. How I validated correctness

- **Compute-core unit tests** (`tests/test_aggregate.py`, `test_query_builder.py`): fixture-based tests of the 5 aggregations and the params builder. Includes per-study country dedupe, phase-missing → `NA`, network edge weights, comparison-axis ordering, and other edge cases.
- **Agent-tool + assembly integration tests** (`tests/test_agent_flow.py`): fake client (fixture) drives the tools in sequence, checking assembly output, citations, the **explicit-filter-wins rule**, no_data, and guards (e.g., aggregating without a search). No LLM/network needed.
- **Real API validation** (`scripts/run_examples.py`): 6 examples (5 categories + an empty-result case) executed against the real CT.gov API and recorded in `examples/example_runs.md`. Verified that the network really links hub sponsors (NCI, Merck, etc.) and that citation `nct_id`s + excerpts match actual studies.
- **API contract sanity-checked up front:** Before writing code, I used `curl` to confirm the field set, `filter.advanced` (phase/date range), `query.locn`, pagination, and the max pageSize.

**All 34 tests pass** (`uv run pytest`).

---

## 6. Limitations & directions for more time

- **`MAX_STUDIES` sampling bias:** Queries exceeding the cap are aggregated on the top-N by relevance, so time_trend in particular is a sample, not a full census (flagged via `capped`). → Improvement: use per-year `countTotal` queries for exact time_trend counts.
- **Multi-hop questions not implemented:** The prompt and examples focus on single-hop questions. The agent shape allows multi-hop ("top sponsors → their trends") in principle, but the dedicated tools and validation were out of scope. → Improvement: add tools that feed intermediate results into a subsequent search, plus stronger loop-prevention.
- **HTTP client:** Calls via `httpx` consistently produced a 403 at CT.gov's edge (suspected TLS fingerprinting), so we switched to `requests`. Root-causing was deferred.
- **LLM live-path example:** Because the submission environment has no API key, `example_runs.md` was generated in `scripted` mode (replaying tool sequences). The data, aggregation, and assembly are all real code/API output; with a key present, the same script runs via `run_agent` (the actual agent).
- **Agent nondeterminism:** ReAct tool selection can vary between runs. Numerical correctness is enforced by the tools, but "which chart type gets picked" can differ — the prompt only guides. → Improvement: post-hoc validation and an eval set for tool selection.

---

## 7. AI-tool usage (integrity note)

- **Tools used:** Claude Code (pair programming / code generation), web search (LangGraph single- vs multi-agent, ReAct tradeoffs).
- **What I designed and decided (deliberate):** Overall architecture, the "LLM orchestrates only · numbers come from tools · response assembled from Session artifacts" principle, the rationale for ReAct and how to wall off its main risk (number generation), the deliberate omission of a name-normalization layer, the response schema and citation bucket-key convention, and the cap/top-N honesty machinery. (Initially built as a deterministic graph; then refactored to a ReAct agent for extensibility while keeping the compute core intact.)
- **What was generated and then adapted (generated & adapted):** Boilerplate for tools/client/aggregation and the test cases. Every API assumption was empirically verified with `curl` before I wrote code, and correctness was validated via unit/integration tests and eyeballing real API output.
