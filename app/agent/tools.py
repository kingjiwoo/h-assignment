"""Unified agent toolset.

One tool = one analysis kind = one chart type. Each tool internally performs
search → aggregate → finalize atomically and leaves a completed Artifact and
final_* state on the Session.

The LLM only picks *which* analysis to run. It has no channel to specify
chart_type directly, which rules out any kind↔chart_type mismatch, and every
number is computed deterministically by the core (app/core) from real data.
"""

from concurrent.futures import ThreadPoolExecutor

from langchain_core.tools import tool

from app.config import settings
from app.core.aggregate import (
    aggregate_comparison,
    aggregate_distribution,
    aggregate_geo,
    aggregate_network,
    aggregate_time_trend,
)
from app.core.query import build_ctgov_params
from app.agent.session import Artifact, SearchResult, Session
from app.services.ctgov_client import CtGovClient

# Chart type each analysis kind commits to — deterministic 1:1 mapping.
# The safety belt in assemble_response re-checks this table so that even
# session-tampering bypasses are caught before rendering.
KIND_TO_CHART: dict[str, str] = {
    "time_trend": "time_series",
    "distribution": "bar_chart",
    "geo": "bar_chart",
    "comparison": "grouped_bar_chart",
    "network": "network_graph",
}

DISTRIBUTION_FIELDS = {"phase", "intervention_type", "status"}
COMPARISON_FIELDS = {"phase", "status"}
NETWORK_DIMENSIONS = {"sponsor_drug", "drug_drug"}


def _merged_filters(session_filters: dict, tool_args: dict) -> dict:
    """Filters declared on the request always win over LLM-supplied values (deterministic guarantee)."""
    merged = dict(tool_args)
    for k, v in session_filters.items():
        if k in merged and v not in (None, ""):
            merged[k] = v
    return merged


def make_tools(session: Session, client: CtGovClient | None = None) -> list:
    """Build a list of tools bound to the given Session (created fresh per request)."""
    client = client or CtGovClient()

    # Per-request cache of CT.gov responses keyed by filter combination.
    # When multiple analyses (e.g., an A/B comparison with a shared filter) hit the
    # same key, the API is only called once.
    fetch_cache: dict[frozenset, tuple[list, bool]] = {}

    def _fetch(filter_kwargs: dict) -> tuple[list, bool, dict, dict]:
        """Search with the given filters (reusing cache) and return (studies, capped, ctgov_params, effective_filters)."""
        merged = _merged_filters(session.input_filters, filter_kwargs)
        effective = {k: v for k, v in merged.items() if v not in (None, "")}
        params = build_ctgov_params(**merged)
        if not params:
            return [], False, {}, effective
        key = frozenset(effective.items())
        if key in fetch_cache:
            studies, capped = fetch_cache[key]
        else:
            studies, capped = client.search_studies(params, max_studies=settings.max_studies)
            fetch_cache[key] = (studies, capped)
        return studies, capped, params, effective

    def _record_search(label: str, studies: list, capped: bool, effective_filters: dict) -> None:
        session.searches[label] = SearchResult(
            label=label, studies=studies, capped=capped, filters=effective_filters
        )
        session.index_studies(studies)
        if capped:
            note = (
                f"Search '{label}' hit the cap (MAX_STUDIES={settings.max_studies}); "
                f"aggregating only the top slice."
            )
            if note not in session.notes:
                session.notes.append(note)

    def _finalize(kind: str, result: dict, title: str, extra: dict | None = None) -> str:
        aid = session.next_artifact_id(kind)
        session.artifacts[aid] = Artifact(
            artifact_id=aid,
            kind=kind,
            data=result["data"],
            buckets=result["buckets"],
            notes=result.get("notes", []),
            extra=extra or {},
        )
        session.final_artifact_id = aid
        session.final_chart_type = KIND_TO_CHART[kind]
        session.final_title = title
        return aid

    _NO_FILTERS_MSG = (
        "No filters provided; cannot build a CT.gov query. "
        "Supply at least one of drug_name/condition/sponsor/country, or call "
        "report_unresolvable if the question does not specify a target."
    )

    @tool
    def analyze_time_trend(
        title: str,
        drug_name: str | None = None,
        condition: str | None = None,
        sponsor: str | None = None,
        country: str | None = None,
        trial_phase: str | None = None,
        start_year: int | None = None,
        end_year: int | None = None,
        overall_status: str | None = None,
    ) -> str:
        """Compute and commit a yearly trial-count trend (time_series).

        Args:
            title: Human-readable chart title.
            drug_name/condition/sponsor/country/trial_phase/start_year/end_year/overall_status:
                CT.gov search filters. At least one is required.
        Returns:
            Summary of the commit (artifact_id, number of data points, search size).
        """
        filter_kwargs = {
            "drug_name": drug_name, "condition": condition, "sponsor": sponsor,
            "country": country, "trial_phase": trial_phase,
            "start_year": start_year, "end_year": end_year,
            "overall_status": overall_status,
        }
        studies, capped, params, effective = _fetch(filter_kwargs)
        if not params:
            return _NO_FILTERS_MSG
        _record_search("default", studies, capped, effective)
        if not studies:
            return f"No trials matched (filters={effective}); no visualization committed."
        result = aggregate_time_trend(studies)
        aid = _finalize("time_trend", result, title)
        return (
            f"Committed time_series: artifact_id='{aid}', {len(result['data'])} years, "
            f"{len(studies)} studies{' (cap reached)' if capped else ''}."
        )

    @tool
    def analyze_distribution(
        field: str,
        title: str,
        drug_name: str | None = None,
        condition: str | None = None,
        sponsor: str | None = None,
        country: str | None = None,
        trial_phase: str | None = None,
        start_year: int | None = None,
        end_year: int | None = None,
        overall_status: str | None = None,
    ) -> str:
        """Compute and commit a category distribution (bar_chart).

        Args:
            field: One of 'phase' | 'intervention_type' | 'status' | 'country'.
                'country' is handled as a geographic distribution (trial count by country).
            title: Chart title.
            (Other search filters are the same as analyze_time_trend.)
        """
        if field != "country" and field not in DISTRIBUTION_FIELDS:
            return (
                f"Unsupported field='{field}'. "
                f"Allowed: {sorted(DISTRIBUTION_FIELDS | {'country'})}"
            )
        filter_kwargs = {
            "drug_name": drug_name, "condition": condition, "sponsor": sponsor,
            "country": country, "trial_phase": trial_phase,
            "start_year": start_year, "end_year": end_year,
            "overall_status": overall_status,
        }
        studies, capped, params, effective = _fetch(filter_kwargs)
        if not params:
            return _NO_FILTERS_MSG
        _record_search("default", studies, capped, effective)
        if not studies:
            return f"No trials matched (filters={effective})."
        if field == "country":
            result = aggregate_geo(studies)
            kind = "geo"
        else:
            result = aggregate_distribution(studies, field)
            kind = "distribution"
        aid = _finalize(kind, result, title, extra={"field": field})
        return (
            f"Committed bar_chart: artifact_id='{aid}', kind={kind}, "
            f"{len(result['data'])} categories, {len(studies)} studies."
        )

    @tool
    def analyze_comparison(
        filter_sets: list[dict],
        title: str,
        field: str = "phase",
    ) -> str:
        """Compare multiple targets side-by-side along a shared axis (grouped_bar_chart).

        Args:
            filter_sets: Filters for each target. At least two entries; each entry is
                {"label": <display>, "drug_name": ..., "condition": ..., ...}.
                Labels must be unique, and each entry needs at least one non-label filter.
            title: Chart title.
            field: Comparison axis. 'phase' (default) or 'status'.
        """
        if len(filter_sets) < 2:
            return "Comparison requires at least 2 filter_sets."
        if field not in COMPARISON_FIELDS:
            return f"Unsupported field='{field}'. Allowed: {sorted(COMPARISON_FIELDS)}"
        labels = [fs.get("label") for fs in filter_sets]
        if any(not lbl for lbl in labels):
            return "Each entry in filter_sets must include a 'label'."
        if len(set(labels)) != len(labels):
            return "Labels in filter_sets must be unique."

        def _one(fs: dict):
            fk = {k: v for k, v in fs.items() if k != "label"}
            return fs["label"], _fetch(fk)

        # Parallel fetch — identical filter combinations get deduped by fetch_cache.
        with ThreadPoolExecutor(max_workers=min(len(filter_sets), 4)) as pool:
            fetched = list(pool.map(_one, filter_sets))

        groups = []
        for label, (studies, capped, params, effective) in fetched:
            if not params:
                return f"Filters for label='{label}' are empty. {_NO_FILTERS_MSG}"
            _record_search(label, studies, capped, effective)
            groups.append({"label": label, "studies": studies})

        if all(len(g["studies"]) == 0 for g in groups):
            return "All targets returned zero results; comparison is not possible."

        result = aggregate_comparison(groups, field=field)
        aid = _finalize(
            "comparison",
            result,
            title,
            extra={"group_labels": result["group_labels"], "field": field},
        )
        return (
            f"Committed grouped_bar_chart: artifact_id='{aid}', "
            f"groups={result['group_labels']}, {len(result['data'])} categories."
        )

    @tool
    def analyze_network(
        dimension: str,
        title: str,
        drug_name: str | None = None,
        condition: str | None = None,
        sponsor: str | None = None,
        country: str | None = None,
        trial_phase: str | None = None,
        start_year: int | None = None,
        end_year: int | None = None,
        overall_status: str | None = None,
    ) -> str:
        """Compute and commit an entity relationship graph (network_graph).

        Args:
            dimension: 'sponsor_drug' (sponsor↔drug) or 'drug_drug'
                (drug↔drug co-occurrence in combination trials).
            title: Chart title.
            (Search filters are the same as analyze_time_trend.)
        """
        if dimension not in NETWORK_DIMENSIONS:
            return f"Unsupported dimension='{dimension}'. Allowed: {sorted(NETWORK_DIMENSIONS)}"
        filter_kwargs = {
            "drug_name": drug_name, "condition": condition, "sponsor": sponsor,
            "country": country, "trial_phase": trial_phase,
            "start_year": start_year, "end_year": end_year,
            "overall_status": overall_status,
        }
        studies, capped, params, effective = _fetch(filter_kwargs)
        if not params:
            return _NO_FILTERS_MSG
        _record_search("default", studies, capped, effective)
        if not studies:
            return f"No trials matched (filters={effective})."
        result = aggregate_network(studies, dimension)
        aid = _finalize("network", result, title, extra={"dimension": dimension})
        return (
            f"Committed network_graph: artifact_id='{aid}', "
            f"{len(result['data']['nodes'])} nodes, {len(result['data']['edges'])} edges."
        )

    @tool
    def report_unresolvable(reason: str, missing: list[str] | None = None) -> str:
        """Call when the question does not let you pinpoint what to query (honest abstention).

        Use this when the target (condition/drug/sponsor/country, etc.) is entirely
        absent or too ambiguous to build a grounded search. Never invent values to
        search with — declare 'unresolvable' via this tool and exit. The server
        forwards this to the user as-is.

        Args:
            reason: One-sentence explanation of why the question can't be resolved.
            missing: Missing items (e.g., ['condition', 'drug_name']).
        Returns:
            Confirmation that the abstention was recorded.
        """
        session.unresolved = {"reason": reason, "missing": missing or []}
        return f"Recorded as unresolvable: {reason}. Do not call any more tools."

    return [
        analyze_time_trend,
        analyze_distribution,
        analyze_comparison,
        analyze_network,
        report_unresolvable,
    ]
