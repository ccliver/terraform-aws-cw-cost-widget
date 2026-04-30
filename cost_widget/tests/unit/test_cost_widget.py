import pytest
from cost_widget.main import (
    get_cost_explorer_data,
    gen_html_report,
    lambda_handler,
    _get_lookback_days,
    _get_granularity,
    _aggregate_results,
    _format_period_label,
)


def test_get_cost_explorer_data(setup_ce):
    data, granularity = get_cost_explorer_data({})

    assert "ResultsByTime" in data
    assert len(data["ResultsByTime"]) == 1
    assert "Groups" in data["ResultsByTime"][0]
    assert len(data["ResultsByTime"][0]["Groups"]) == 7
    assert granularity == "MONTHLY"


def test_gen_html_report(setup_ce):
    data, granularity = get_cost_explorer_data({})
    html_report = gen_html_report(data, granularity)

    assert "<html>" in html_report
    assert "<table>" in html_report
    assert "AmazonCloudWatch" not in html_report
    assert "EC2 - Other" in html_report
    assert "Amazon Elastic Container Service for Kubernetes" in html_report
    assert "Amazon Elastic Compute Cloud - Compute" in html_report
    assert "Amazon Simple Storage Service" in html_report
    assert "AWS Key Management Service" in html_report
    assert "Cost Over Time" in html_report
    assert "Cost by Service" in html_report
    assert "Total" in html_report
    assert "vs Prior Period" not in html_report


def test_gen_html_report_empty_groups(setup_ce):
    data, granularity = get_cost_explorer_data({})
    data["ResultsByTime"][0]["Groups"] = []

    html_report = gen_html_report(data, granularity)

    assert "No costs found" in html_report


def test_lambda_handler(setup_ce):
    html_report = lambda_handler({}, None)

    assert "<html>" in html_report
    assert "EC2 - Other" in html_report
    assert "Amazon Elastic Container Service for Kubernetes" in html_report
    assert "Amazon Elastic Compute Cloud - Compute" in html_report
    assert "Amazon Simple Storage Service" in html_report
    assert "AWS Key Management Service" in html_report
    assert "Cost Over Time" in html_report
    assert "Cost by Service" in html_report
    assert "Total" in html_report
    assert "AmazonCloudWatch" not in html_report


# --- _get_lookback_days ---


def test_get_lookback_days_from_event_params():
    assert (
        _get_lookback_days({"widgetContext": {"params": {"lookback_days": 14}}}) == 14
    )


def test_get_lookback_days_string_param():
    assert (
        _get_lookback_days({"widgetContext": {"params": {"lookback_days": "60"}}}) == 60
    )


def test_get_lookback_days_from_env(monkeypatch):
    monkeypatch.setenv("DEFAULT_LOOKBACK_DAYS", "45")
    assert _get_lookback_days({}) == 45


def test_get_lookback_days_default(monkeypatch):
    monkeypatch.delenv("DEFAULT_LOOKBACK_DAYS", raising=False)
    assert _get_lookback_days({}) == 30


def test_get_lookback_days_event_overrides_env(monkeypatch):
    monkeypatch.setenv("DEFAULT_LOOKBACK_DAYS", "90")
    assert _get_lookback_days({"widgetContext": {"params": {"lookback_days": 7}}}) == 7


def test_get_lookback_days_negative_raises():
    with pytest.raises(ValueError):
        _get_lookback_days({"widgetContext": {"params": {"lookback_days": -1}}})


def test_get_lookback_days_zero_raises():
    with pytest.raises(ValueError):
        _get_lookback_days({"widgetContext": {"params": {"lookback_days": 0}}})


# --- _get_granularity ---


def test_get_granularity_daily_from_event():
    assert (
        _get_granularity({"widgetContext": {"params": {"granularity": "DAILY"}}})
        == "DAILY"
    )


def test_get_granularity_monthly_from_event():
    assert (
        _get_granularity({"widgetContext": {"params": {"granularity": "MONTHLY"}}})
        == "MONTHLY"
    )


def test_get_granularity_case_insensitive():
    assert (
        _get_granularity({"widgetContext": {"params": {"granularity": "daily"}}})
        == "DAILY"
    )


def test_get_granularity_from_env(monkeypatch):
    monkeypatch.setenv("DEFAULT_GRANULARITY", "DAILY")
    assert _get_granularity({}) == "DAILY"


def test_get_granularity_default(monkeypatch):
    monkeypatch.delenv("DEFAULT_GRANULARITY", raising=False)
    assert _get_granularity({}) == "MONTHLY"


def test_get_granularity_invalid_raises():
    with pytest.raises(ValueError):
        _get_granularity({"widgetContext": {"params": {"granularity": "WEEKLY"}}})


# --- _format_period_label ---


def test_format_period_label_monthly():
    assert (
        _format_period_label({"Start": "2026-04-01", "End": "2026-05-01"}, "MONTHLY")
        == "Apr 2026"
    )


def test_format_period_label_daily():
    assert (
        _format_period_label({"Start": "2026-04-29", "End": "2026-04-30"}, "DAILY")
        == "Apr 29"
    )


def test_format_period_label_monthly_jan():
    assert (
        _format_period_label({"Start": "2026-01-01", "End": "2026-02-01"}, "MONTHLY")
        == "Jan 2026"
    )


# --- _aggregate_results ---


def test_aggregate_results_single_bucket():
    results = [
        {"Groups": [{"Keys": ["EC2"], "Metrics": {"BlendedCost": {"Amount": "10.0"}}}]}
    ]
    totals, grand = _aggregate_results(results)
    assert totals == {"EC2": 10.0}
    assert grand == 10.0


def test_aggregate_results_multi_bucket():
    bucket = {
        "Groups": [{"Keys": ["EC2"], "Metrics": {"BlendedCost": {"Amount": "5.0"}}}]
    }
    totals, grand = _aggregate_results([bucket, bucket])
    assert totals == {"EC2": 10.0}
    assert grand == 10.0


def test_aggregate_results_multiple_services():
    results = [
        {
            "Groups": [
                {"Keys": ["EC2"], "Metrics": {"BlendedCost": {"Amount": "3.0"}}},
                {"Keys": ["S3"], "Metrics": {"BlendedCost": {"Amount": "1.0"}}},
            ]
        },
        {
            "Groups": [
                {"Keys": ["EC2"], "Metrics": {"BlendedCost": {"Amount": "2.0"}}},
                {"Keys": ["S3"], "Metrics": {"BlendedCost": {"Amount": "0.5"}}},
            ]
        },
    ]
    totals, grand = _aggregate_results(results)
    assert totals == {"EC2": 5.0, "S3": 1.5}
    assert grand == 6.5


def test_aggregate_results_empty_groups():
    totals, grand = _aggregate_results([{"Groups": []}])
    assert totals == {}
    assert grand == 0.0
