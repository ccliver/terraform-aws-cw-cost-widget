import moto
import pytest

from cost_widget.main import get_cost_explorer_data, gen_html_report, lambda_handler


def test_get_cost_explorer_data(setup_ce):
    """Test get_cost_explorer_data function"""

    cost_data = get_cost_explorer_data()

    assert "ResultsByTime" in cost_data
    assert len(cost_data["ResultsByTime"]) == 1
    assert "Groups" in cost_data["ResultsByTime"][0]
    assert len(cost_data["ResultsByTime"][0]["Groups"]) == 7


def test_gen_html_report(setup_ce):
    """Test gen_html_report function"""

    cost_data = get_cost_explorer_data()
    html_report = gen_html_report(cost_data)

    assert "<html>" in html_report
    assert "<table style='border: 1px solid black;'>" in html_report
    assert "AWS Key Management Service" in html_report
    assert "EC2 - Other" in html_report
    assert "Amazon Elastic Compute Cloud - Compute" in html_report
    assert "Amazon Elastic Container Service for Kubernetes" in html_report
    assert "Amazon Simple Storage Service" in html_report
    assert "Total" in html_report


def test_lambda_handler(setup_ce):
    """Test lambda_handler function"""

    event = {}
    context = None

    html_report = lambda_handler(event, context)

    assert "<html>" in html_report
    assert "<table style='border: 1px solid black;'>" in html_report
    assert "AWS Key Management Service" in html_report
    assert "EC2 - Other" in html_report
    assert "Amazon Elastic Compute Cloud - Compute" in html_report
    assert "Amazon Elastic Container Service for Kubernetes" in html_report
    assert "Amazon Simple Storage Service" in html_report
    assert "Total" in html_report
