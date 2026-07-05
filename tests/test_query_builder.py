"""Parameter-mapping tests for the query builder."""

from app.core.query import build_ctgov_params


def test_basic_text_filters():
    params = build_ctgov_params(drug_name="Pembrolizumab", condition="Melanoma")
    assert params["query.intr"] == "Pembrolizumab"
    assert params["query.cond"] == "Melanoma"


def test_country_and_status():
    params = build_ctgov_params(country="Canada", overall_status="RECRUITING")
    assert params["query.locn"] == "Canada"
    assert params["filter.overallStatus"] == "RECRUITING"


def test_phase_and_year_range_go_into_advanced_filter():
    params = build_ctgov_params(trial_phase="PHASE3", start_year=2015, end_year=2020)
    adv = params["filter.advanced"]
    assert "AREA[Phase]PHASE3" in adv
    assert "AREA[StartDate]RANGE[2015-01-01,2020-12-31]" in adv
    assert " AND " in adv


def test_open_ended_year_range():
    params = build_ctgov_params(start_year=2018)
    assert "RANGE[2018-01-01,MAX]" in params["filter.advanced"]


def test_empty_when_no_filters():
    assert build_ctgov_params() == {}
