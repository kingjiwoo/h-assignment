"""study(protocolSection dict)에서 관심 필드를 안전하게 꺼내는 헬퍼 모음.

CT.gov 응답은 모듈/필드가 누락될 수 있으므로(예: designModule 없음, collaborators 없음)
모든 접근을 방어적으로 처리한다. 집계 함수와 citation 부착이 공통으로 사용한다.
"""


def nct_id(study: dict) -> str:
    return study.get("identificationModule", {}).get("nctId", "")


def brief_title(study: dict) -> str:
    return study.get("identificationModule", {}).get("briefTitle", "")


def overall_status(study: dict) -> str | None:
    return study.get("statusModule", {}).get("overallStatus")


def start_year(study: dict) -> int | None:
    date = study.get("statusModule", {}).get("startDateStruct", {}).get("date")
    if not date:
        return None
    try:
        return int(date[:4])
    except (ValueError, TypeError):
        return None


def phases(study: dict) -> list[str]:
    """phase 리스트. 없으면 ['NA']로 정규화한다 (CT.gov도 미지정을 NA로 취급)."""
    ph = study.get("designModule", {}).get("phases")
    return ph if ph else ["NA"]


def lead_sponsor(study: dict) -> str | None:
    return study.get("sponsorCollaboratorsModule", {}).get("leadSponsor", {}).get("name")


def conditions(study: dict) -> list[str]:
    return study.get("conditionsModule", {}).get("conditions", []) or []


def interventions(study: dict) -> list[dict]:
    """[{type, name}] 리스트. 없으면 빈 리스트."""
    return study.get("armsInterventionsModule", {}).get("interventions", []) or []


def drug_names(study: dict) -> list[str]:
    """type이 DRUG 또는 BIOLOGICAL인 중재명만 (drug↔drug 네트워크 재료)."""
    names = []
    for iv in interventions(study):
        if iv.get("type") in ("DRUG", "BIOLOGICAL") and iv.get("name"):
            names.append(iv["name"])
    return names


def intervention_types(study: dict) -> list[str]:
    return [iv["type"] for iv in interventions(study) if iv.get("type")]


def countries(study: dict) -> list[str]:
    """study가 진행되는 국가들(중복 제거). 한 study가 여러 국가를 가질 수 있다."""
    locs = study.get("contactsLocationsModule", {}).get("locations", []) or []
    seen = []
    for loc in locs:
        c = loc.get("country")
        if c and c not in seen:
            seen.append(c)
    return seen
