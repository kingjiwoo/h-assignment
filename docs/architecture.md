# System architecture

## 1. Constrained ReAct agent

The LLM only owns **tool orchestration** (choosing what to search and which aggregation
to combine). **Every number is computed by deterministic tools.** The final response is
assembled by the server straight out of Session artifacts — not from LLM text.

```mermaid
flowchart TD
    Client([POST /query<br/>query + optional filters]) --> Agent

    subgraph AgentLoop["🧠 create_react_agent (LLM decides order and combinations)"]
        Agent["ReAct loop<br/>Pick and call a tool →<br/>observe the summary (preview) → decide next"]
    end

    Agent -->|call| Tools

    subgraph Tools["🛠 Tools (every number is computed here, deterministically)"]
        T1["analyze_time_trend<br/>CT.gov search + yearly aggregation<br/>→ time_series"]
        T2["analyze_distribution<br/>phase/intervention_type/status/country<br/>→ bar_chart"]
        T3["analyze_comparison<br/>parallel searches compared on a shared axis<br/>→ grouped_bar_chart"]
        T4["analyze_network<br/>sponsor↔drug / drug↔drug<br/>→ network_graph"]
        T5["report_unresolvable<br/>honest abstention"]
    end

    Tools -->|"stores numbers/buckets<br/>(returns only preview to the LLM)"| Session[("Session<br/>searches · artifacts<br/>studies_by_nct")]
    T1 <-->|HTTP| CTGov[("ClinicalTrials.gov<br/>v2 API")]

    Session -->|"the server pulls the<br/>committed artifact directly"| Assemble["assemble_response<br/>visualization + meta + citations"]
    Assemble --> Response([Structured JSON response])

    style AgentLoop fill:#f0f7ff,stroke:#3b82f6,stroke-dasharray:5 5
    style Tools fill:#f5fff0,stroke:#22c55e,stroke-dasharray:5 5
    style Session fill:#fef9e7,stroke:#eab308
    style CTGov fill:#fff7ed,stroke:#f97316
```

## 2. Why this shape — separating extensibility from safety

```mermaid
flowchart LR
    subgraph Judgment["🧠 What the LLM does (judgment / composition)"]
        A1["Parse the question → pick a tool"]
        A2["Decide search filters"]
        A3["Choose the aggregation axis / chart type / title"]
        A4["Compose multi-step flows (room to extend)"]
    end
    subgraph Compute["🛠 What the tools / core do (compute)"]
        B1["API query and pagination"]
        B2["group-by · count (every number)"]
        B3["network edges and weights"]
        B4["citation mapping"]
    end
    Judgment -->|"tool call"| Compute
    Compute -->|"artifact (real numbers)"| Store[("Session")]
    Store -->|"server assembles"| Out([Response])

    style Judgment fill:#f0f7ff,stroke:#3b82f6
    style Compute fill:#f5fff0,stroke:#22c55e
    style Store fill:#fef9e7,stroke:#eab308
```

> **Extensibility** comes from letting the LLM combine tools at runtime (new combinations
> and multi-hop flows without code changes), while **correctness/safety** comes from
> walling numbers off inside tools and assembling responses from artifacts.
> Because the two concerns are separated, the compute core (`app/core`) and its tests
> are unaffected when you swap out the orchestration.

## 3. Layer layout

```mermaid
flowchart TD
    subgraph API["app/main.py"]
        M["FastAPI · request validation · explicit-filter extraction"]
    end
    subgraph Orchestration["app/agent/"]
        R["runner (agent execution + response assembly)"]
        TL["tools (@tool set, bound to Session)"]
        SE["session (per-request state)"]
    end
    subgraph Core["app/core/ (LLM-independent · fully unit-tested)"]
        AG["aggregate (5 pure aggregations)"]
        EX["extractors (field extraction)"]
        QB["query (params builder)"]
    end
    subgraph Services["app/services/"]
        CC["ctgov_client (requests)"]
        LM["llm (provider-agnostic)"]
    end

    M --> R --> TL --> AG
    TL --> QB
    AG --> EX
    TL --> CC
    R --> LM
```

**Design principle:** separate orchestration (`agent`) from compute (`core`). The first
iteration used a deterministic LangGraph; the orchestration was then replaced with a
ReAct agent to gain extensibility while the compute core and its tests were reused as-is.
