"""Helpers to safely pull fields of interest out of a study (protocolSection dict).

CT.gov responses may omit modules/fields (e.g., no designModule, no collaborators),
so every access is defensive. Shared by the aggregation functions and citation assembly.
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
    """List of phases; normalized to ['NA'] when missing (CT.gov also treats unspecified as NA)."""
    ph = study.get("designModule", {}).get("phases")
    return ph if ph else ["NA"]


def lead_sponsor(study: dict) -> str | None:
    return study.get("sponsorCollaboratorsModule", {}).get("leadSponsor", {}).get("name")


def conditions(study: dict) -> list[str]:
    return study.get("conditionsModule", {}).get("conditions", []) or []


def interventions(study: dict) -> list[dict]:
    """List of [{type, name}]; empty list if none."""
    return study.get("armsInterventionsModule", {}).get("interventions", []) or []


def drug_names(study: dict) -> list[str]:
    """Names of interventions whose type is DRUG or BIOLOGICAL (input for drug↔drug networks)."""
    names = []
    for iv in interventions(study):
        if iv.get("type") in ("DRUG", "BIOLOGICAL") and iv.get("name"):
            names.append(iv["name"])
    return names


def intervention_types(study: dict) -> list[str]:
    return [iv["type"] for iv in interventions(study) if iv.get("type")]


def countries(study: dict) -> list[str]:
    """Countries the study is conducted in (deduped). A study can span multiple countries."""
    locs = study.get("contactsLocationsModule", {}).get("locations", []) or []
    seen = []
    for loc in locs:
        c = loc.get("country")
        if c and c not in seen:
            seen.append(c)
    return seen
