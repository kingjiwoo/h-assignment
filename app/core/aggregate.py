"""Aggregation functions — all pure. No LLM/network dependency; unit-testable offline.

Each function returns:
    {"data": <chart data>, "buckets": {bucket_key: [nct_id, ...]}, "notes": [...]}
`buckets` is used to look up the source studies for each data point when attaching citations.

This module is the deterministic "compute core," independent of any orchestration
(agent/graph). Agent tools (app/agent/tools.py) call these functions, and every
number is computed here — the LLM has no path to fabricate a number.
"""

from collections import Counter, defaultdict

from app.core import extractors as ex

PHASE_ORDER = ["EARLY_PHASE1", "PHASE1", "PHASE2", "PHASE3", "PHASE4", "NA"]


def _bucket_by_field(studies: list[dict], field: str) -> dict[str, list[str]]:
    """Bucket studies by the given field value → {category: [nct_id, ...]}.

    Supported fields: 'phase' | 'intervention_type' | 'status'.
    phases() already normalizes missing values to ['NA']; status None becomes 'UNKNOWN'.
    intervention_type dedupes within a study so the same type only counts once per study.
    """
    buckets: dict[str, list[str]] = defaultdict(list)
    for s in studies:
        nct = ex.nct_id(s)
        if field == "phase":
            for ph in ex.phases(s):
                buckets[ph].append(nct)
        elif field == "intervention_type":
            for t in set(ex.intervention_types(s)):
                buckets[t].append(nct)
        elif field == "status":
            st = ex.overall_status(s) or "UNKNOWN"
            buckets[st].append(nct)
    return buckets


def aggregate_time_trend(studies: list[dict]) -> dict:
    """Trial count by start year."""
    buckets: dict[str, list[str]] = defaultdict(list)
    for s in studies:
        y = ex.start_year(s)
        if y is None:
            continue
        buckets[str(y)].append(ex.nct_id(s))

    data = [
        {"year": int(year), "trial_count": len(ncts)}
        for year, ncts in sorted(buckets.items(), key=lambda kv: int(kv[0]))
    ]
    parsed = sum(len(v) for v in buckets.values())
    notes = [f"Based on {parsed} of {len(studies)} studies with parseable StartDate."]
    return {"data": data, "buckets": dict(buckets), "notes": notes}


def aggregate_distribution(studies: list[dict], field: str = "phase") -> dict:
    """Trial count distribution by phase / intervention_type / status."""
    buckets = _bucket_by_field(studies, field)

    if field == "phase":
        keys = sorted(buckets, key=lambda k: PHASE_ORDER.index(k) if k in PHASE_ORDER else 99)
    else:
        keys = sorted(buckets, key=lambda k: len(buckets[k]), reverse=True)

    data = [{"category": k, "trial_count": len(buckets[k])} for k in keys]
    notes = [f"Aggregated {len(studies)} studies (after filtering, field={field})."]
    return {"data": data, "buckets": dict(buckets), "notes": notes}


def aggregate_comparison(groups: list[dict], field: str = "phase") -> dict:
    """Aggregate several groups side-by-side along a shared axis (default phase) — grouped bar chart.

    groups: [{"label": str, "studies": [study, ...]}, ...]
    """
    all_categories: list[str] = []
    per_group: dict[str, dict[str, list[str]]] = {}

    for g in groups:
        label = g["label"]
        cat_buckets = _bucket_by_field(g["studies"], field)
        per_group[label] = cat_buckets
        for c in cat_buckets:
            if c not in all_categories:
                all_categories.append(c)

    if field == "phase":
        all_categories.sort(key=lambda k: PHASE_ORDER.index(k) if k in PHASE_ORDER else 99)

    data = []
    buckets: dict[str, list[str]] = {}
    for cat in all_categories:
        row = {"category": cat}
        for label, cat_buckets in per_group.items():
            row[label] = len(cat_buckets.get(cat, []))
            buckets[f"{label}|{cat}"] = cat_buckets.get(cat, [])
        data.append(row)

    totals = ", ".join(f"{g['label']}: {len(g['studies'])} studies" for g in groups)
    notes = [f"Aggregated targets — {totals} (field={field})."]
    return {
        "data": data,
        "buckets": buckets,
        "group_labels": list(per_group.keys()),
        "notes": notes,
    }


def aggregate_geo(studies: list[dict], top_n: int = 25) -> dict:
    """Trial count by country. A study spanning multiple countries counts once per country.

    Returns only the top_n countries (for readability and response size); exceedance is noted.
    """
    buckets: dict[str, list[str]] = defaultdict(list)
    for s in studies:
        nct = ex.nct_id(s)
        for c in ex.countries(s):  # extractors.countries already dedupes within a study
            buckets[c].append(nct)

    keys = sorted(buckets, key=lambda k: len(buckets[k]), reverse=True)
    notes = []
    if len(keys) > top_n:
        notes.append(f"Showing top {top_n} of {len(keys)} countries.")
        keys = keys[:top_n]

    data = [{"country": k, "trial_count": len(buckets[k])} for k in keys]
    kept_buckets = {k: buckets[k] for k in keys}
    return {"data": data, "buckets": kept_buckets, "notes": notes}


def aggregate_network(
    studies: list[dict], dimension: str = "sponsor_drug", max_edges: int = 60
) -> dict:
    """Entity relationship graph.

    - sponsor_drug: leadSponsor.name ↔ each DRUG intervention name
    - drug_drug: two or more DRUG interventions in the same study → all pairs as co-occurrence edges
    Each edge carries a weight (number of shared studies) and its source nct_ids. For response
    size and readability, only the top max_edges (by weight) edges are kept, and only nodes
    incident to those edges are returned (degree is recomputed on the retained edges).
    Exceedance is noted.
    """
    edge_ncts: dict[tuple[str, str], list[str]] = defaultdict(list)
    node_kind: dict[str, str] = {}

    for s in studies:
        nct = ex.nct_id(s)
        if dimension == "sponsor_drug":
            sponsor = ex.lead_sponsor(s)
            if not sponsor:
                continue
            node_kind[sponsor] = "sponsor"
            for drug in set(ex.drug_names(s)):
                node_kind[drug] = "drug"
                edge_ncts[(sponsor, drug)].append(nct)
        elif dimension == "drug_drug":
            drugs = sorted(set(ex.drug_names(s)))
            for d in drugs:
                node_kind[d] = "drug"
            for i in range(len(drugs)):
                for j in range(i + 1, len(drugs)):
                    edge_ncts[(drugs[i], drugs[j])].append(nct)

    sorted_edges = sorted(edge_ncts.items(), key=lambda kv: len(kv[1]), reverse=True)
    notes = []
    if len(sorted_edges) > max_edges:
        notes.append(
            f"Showing top {max_edges} of {len(sorted_edges)} edges by weight (hub-focused graph)."
        )
        sorted_edges = sorted_edges[:max_edges]

    edges = []
    buckets: dict[str, list[str]] = {}
    degree: Counter = Counter()
    kept_nodes: set[str] = set()
    for (src, tgt), ncts in sorted_edges:
        edges.append({"source": src, "target": tgt, "weight": len(ncts)})
        buckets[f"{src}|{tgt}"] = ncts
        degree[src] += len(ncts)
        degree[tgt] += len(ncts)
        kept_nodes.add(src)
        kept_nodes.add(tgt)

    nodes = [
        {"id": n, "kind": node_kind[n], "degree": degree[n]}
        for n in sorted(kept_nodes, key=lambda n: degree[n], reverse=True)
    ]

    return {"data": {"nodes": nodes, "edges": edges}, "buckets": buckets, "notes": notes}
