"""집계 함수 단위 테스트 — 네트워크/LLM 없이 fixture만으로 검증."""

import json
from pathlib import Path

from app.graph.nodes.aggregate import (
    aggregate_comparison,
    aggregate_distribution,
    aggregate_geo,
    aggregate_network,
    aggregate_time_trend,
)

FIXTURE = json.loads((Path(__file__).parent / "fixtures" / "sample_studies.json").read_text())


def test_time_trend_counts_by_start_year():
    result = aggregate_time_trend(FIXTURE)
    counts = {row["year"]: row["trial_count"] for row in result["data"]}
    assert counts == {2015: 2, 2020: 1}
    # 연도 오름차순 정렬 확인
    assert [r["year"] for r in result["data"]] == [2015, 2020]
    # citation용 버킷에 nct_id가 담긴다
    assert set(result["buckets"]["2015"]) == {"NCT001", "NCT002"}


def test_distribution_by_phase_normalizes_missing_to_na():
    result = aggregate_distribution(FIXTURE, "phase")
    counts = {row["category"]: row["trial_count"] for row in result["data"]}
    assert counts == {"PHASE2": 1, "PHASE3": 1, "NA": 1}


def test_distribution_by_intervention_type():
    result = aggregate_distribution(FIXTURE, "intervention_type")
    counts = {row["category"]: row["trial_count"] for row in result["data"]}
    assert counts["DRUG"] == 2
    assert counts["DEVICE"] == 1


def test_geo_dedupes_country_within_study():
    result = aggregate_geo(FIXTURE)
    counts = {row["country"]: row["trial_count"] for row in result["data"]}
    # NCT003은 Canada가 두 번 나오지만 study 단위로 1회만 카운트
    assert counts["Canada"] == 2
    assert counts["United States"] == 2


def test_network_sponsor_drug_edges_and_weights():
    result = aggregate_network(FIXTURE, "sponsor_drug")
    edges = {(e["source"], e["target"]): e["weight"] for e in result["data"]["edges"]}
    # Sponsor X가 DrugA를 2개 study에서 사용 → weight 2
    assert edges[("Sponsor X", "DrugA")] == 2
    assert edges[("Sponsor X", "DrugB")] == 1
    node_ids = {n["id"] for n in result["data"]["nodes"]}
    assert {"Sponsor X", "DrugA", "DrugB", "DrugC"} <= node_ids


def test_network_drug_drug_cooccurrence():
    result = aggregate_network(FIXTURE, "drug_drug")
    edges = {(e["source"], e["target"]): e["weight"] for e in result["data"]["edges"]}
    # NCT001: DrugA-DrugB, NCT002: DrugA-DrugC
    assert edges[("DrugA", "DrugB")] == 1
    assert edges[("DrugA", "DrugC")] == 1


def test_comparison_groups_share_phase_axis():
    groups = [
        {"label": "Group1", "studies": [FIXTURE[0]]},  # PHASE3
        {"label": "Group2", "studies": [FIXTURE[1]]},  # PHASE2
    ]
    result = aggregate_comparison(groups, "phase")
    assert result["group_labels"] == ["Group1", "Group2"]
    rows = {row["category"]: row for row in result["data"]}
    assert rows["PHASE3"]["Group1"] == 1
    assert rows["PHASE3"]["Group2"] == 0
    assert rows["PHASE2"]["Group2"] == 1
