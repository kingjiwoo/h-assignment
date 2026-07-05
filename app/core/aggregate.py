"""집계 함수 — 전부 순수 함수. LLM/네트워크 의존 없음, 오프라인 단위테스트 가능.

각 함수는 다음 형태를 반환한다:
    {"data": <chart data>, "buckets": {bucket_key: [nct_id, ...]}, "notes": [...]}
buckets는 citation 부착 시 각 데이터 포인트의 근거 study를 찾는 데 쓰인다.

이 모듈은 오케스트레이션(에이전트/그래프)과 무관한 "계산 코어"다. 에이전트 도구(app/agent/tools.py)가
이 함수들을 호출하며, 모든 수치는 여기서 결정론적으로 계산된다(LLM이 숫자를 만들 경로 없음).
"""

from collections import Counter, defaultdict

from app.core import extractors as ex

PHASE_ORDER = ["EARLY_PHASE1", "PHASE1", "PHASE2", "PHASE3", "PHASE4", "NA"]


def aggregate_time_trend(studies: list[dict]) -> dict:
    """연도별 시작 시험 수."""
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
    return {"data": data, "buckets": dict(buckets), "notes": []}


def aggregate_distribution(studies: list[dict], field: str = "phase") -> dict:
    """phase / intervention_type / status 별 시험 수 분포."""
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

    if field == "phase":
        keys = sorted(buckets, key=lambda k: PHASE_ORDER.index(k) if k in PHASE_ORDER else 99)
    else:
        keys = sorted(buckets, key=lambda k: len(buckets[k]), reverse=True)

    data = [{"category": k, "trial_count": len(buckets[k])} for k in keys]
    return {"data": data, "buckets": dict(buckets), "notes": []}


def aggregate_comparison(groups: list[dict], field: str = "phase") -> dict:
    """여러 그룹을 같은 축(기본 phase)으로 나란히 집계 → grouped bar chart용.

    groups: [{"label": str, "studies": [study, ...]}, ...]
    """
    all_categories: list[str] = []
    per_group: dict[str, dict[str, list[str]]] = {}

    for g in groups:
        label = g["label"]
        cat_buckets: dict[str, list[str]] = defaultdict(list)
        for s in g["studies"]:
            nct = ex.nct_id(s)
            if field == "phase":
                for ph in ex.phases(s):
                    cat_buckets[ph].append(nct)
            elif field == "status":
                st = ex.overall_status(s) or "UNKNOWN"
                cat_buckets[st].append(nct)
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

    return {
        "data": data,
        "buckets": buckets,
        "group_labels": list(per_group.keys()),
        "notes": [],
    }


def aggregate_geo(studies: list[dict], top_n: int = 25) -> dict:
    """국가별 시험 수. 한 study가 여러 국가를 가지면 각 국가에 study 단위로 1회 카운트.

    가독성/응답 크기를 위해 상위 top_n개 국가만 반환한다(초과 시 note로 표기).
    """
    buckets: dict[str, list[str]] = defaultdict(list)
    for s in studies:
        nct = ex.nct_id(s)
        for c in ex.countries(s):  # extractors.countries가 이미 study 내 중복 제거
            buckets[c].append(nct)

    keys = sorted(buckets, key=lambda k: len(buckets[k]), reverse=True)
    notes = []
    if len(keys) > top_n:
        notes.append(f"국가 {len(keys)}개 중 상위 {top_n}개만 표시합니다.")
        keys = keys[:top_n]

    data = [{"country": k, "trial_count": len(buckets[k])} for k in keys]
    kept_buckets = {k: buckets[k] for k in keys}
    return {"data": data, "buckets": kept_buckets, "notes": notes}


def aggregate_network(
    studies: list[dict], dimension: str = "sponsor_drug", max_edges: int = 60
) -> dict:
    """엔티티 관계망.

    - sponsor_drug: leadSponsor.name ↔ 각 DRUG intervention name
    - drug_drug: 같은 study 내 DRUG intervention 2개 이상 → 모든 쌍을 co-occurrence 엣지로
    엣지에는 weight(공유 study 수)와 근거 nct_id를 담는다. 응답 크기·가독성을 위해 weight
    상위 max_edges개 엣지만 남기고, 남은 엣지에 연결된 노드만 반환한다(degree는 남은 엣지 기준
    재계산). 초과 시 note로 표기한다.
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
            f"엣지 {len(sorted_edges)}개 중 가중치 상위 {max_edges}개만 표시합니다(허브 중심 관계망)."
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
