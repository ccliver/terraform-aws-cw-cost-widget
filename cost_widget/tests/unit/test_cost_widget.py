import pytest

from cost_widget.main import get_cost_explorer_data, gen_html_report, lambda_handler


def test_get_cost_explorer_data(setup_ce):
    """Test get_cost_explorer_data function"""

    current, previous = get_cost_explorer_data()

    assert "ResultsByTime" in current
    assert len(current["ResultsByTime"]) == 1
    assert "Groups" in current["ResultsByTime"][0]
    assert len(current["ResultsByTime"][0]["Groups"]) == 7

    assert "ResultsByTime" in previous


def test_gen_html_report(setup_ce):
    """Test gen_html_report function"""

    current, previous = get_cost_explorer_data()
    html_report = gen_html_report(current, previous)

    assert "<html>" in html_report
    assert "<table>" in html_report
    # Zero-cost service should be filtered out
    assert "AmazonCloudWatch" not in html_report
    # Services should be present (sorted by cost descending)
    assert "EC2 - Other" in html_report
    assert "Amazon Elastic Container Service for Kubernetes" in html_report
    assert "Amazon Elastic Compute Cloud - Compute" in html_report
    assert "Amazon Simple Storage Service" in html_report
    assert "AWS Key Management Service" in html_report
    # Delta column header
    assert "vs Prior Month" in html_report
    assert "Total" in html_report


def test_gen_html_report_empty_groups(setup_ce):
    """Test gen_html_report handles empty cost data gracefully"""

    current, previous = get_cost_explorer_data()
    current["ResultsByTime"][0]["Groups"] = []

    html_report = gen_html_report(current, previous)

    assert "No costs found" in html_report


def test_lambda_handler(setup_ce):
    """Test lambda_handler function"""

    html_report = lambda_handler({}, None)

    assert "<html>" in html_report
    assert "EC2 - Other" in html_report
    assert "Amazon Elastic Container Service for Kubernetes" in html_report
    assert "Amazon Elastic Compute Cloud - Compute" in html_report
    assert "Amazon Simple Storage Service" in html_report
    assert "AWS Key Management Service" in html_report
    assert "Total" in html_report
    assert "AmazonCloudWatch" not in html_report
