import datetime
import os

import boto3

from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools import Logger
from botocore.exceptions import ClientError


logger = Logger()
ce = boto3.client("ce", region_name=os.environ.get("AWS_REGION", "us-east-1"))


def get_cost_explorer_data() -> dict:
    """Return dict of Cost Explorer data from the last month"""

    today = datetime.date.today()
    first = today.replace(day=1)
    last_month = first - datetime.timedelta(days=1)
    if "COST_ALLOCATION_TAG" not in os.environ:
        raise ValueError("COST_ALLOCATION_TAG environment variable is not set")
    cost_allocation_tag_key, cost_allocation_tag_value = os.environ[
        "COST_ALLOCATION_TAG"
    ].split("=")

    try:
        total_cost = ce.get_cost_and_usage(
            TimePeriod={
                "Start": f"{last_month.strftime('%Y')}-{last_month.strftime('%m')}-01",
                "End": f"{today.strftime('%Y')}-{today.strftime('%m')}-01",
            },
            Granularity="MONTHLY",
            Metrics=["BlendedCost"],
            Filter={
                "Tags": {
                    "Key": cost_allocation_tag_key,
                    "Values": [cost_allocation_tag_value],
                    "MatchOptions": ["EQUALS"],
                }
            },
        )["ResultsByTime"][0]["Total"]

        cost_by_service = ce.get_cost_and_usage(
            TimePeriod={
                "Start": f"{last_month.strftime('%Y')}-{last_month.strftime('%m')}-01",
                "End": f"{today.strftime('%Y')}-{today.strftime('%m')}-01",
            },
            Granularity="MONTHLY",
            Metrics=["BlendedCost"],
            Filter={
                "Tags": {
                    "Key": cost_allocation_tag_key,
                    "Values": [cost_allocation_tag_value],
                    "MatchOptions": ["EQUALS"],
                }
            },
            GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
        )
        cost_by_service["Total"] = total_cost

    except ClientError as e:
        logger.error(f"Error fetching Cost Explorer data: {e}")
        raise

    logger.debug(f"Cost Explorer data: {cost_by_service}")
    return cost_by_service


def gen_html_report(cost_data: dict) -> str:
    """Generate HTML report from Cost Explorer data"""

    time_period = cost_data["ResultsByTime"][0]["TimePeriod"]
    html = "<html><body>"
    html += "<h1>AWS Cost Report</h1>"
    html += f"<strong>{time_period['Start']} to {time_period['End']}</strong><br><br>"
    html += "<table style='border: 1px solid black;'><tr><th>Service</th><th>Cost (USD)</th></tr>"

    for service in cost_data["ResultsByTime"][0]["Groups"]:
        cost = float(service["Metrics"]["BlendedCost"]["Amount"])
        html += f"<tr><td>{service['Keys'][0]}</td><td>${cost:.2f}</td></tr>"

    html += f"<tr><td><strong>Total</strong></td><td><strong>${float(cost_data['Total']['BlendedCost']['Amount']):.2f}</strong></td></tr>"
    html += "</table></body></html>"

    logger.info("Generated HTML report: " + html)
    return html


def lambda_handler(event: dict, context: LambdaContext) -> str:
    """Lambda function handler to generate AWS Cost Report"""

    cost_data = get_cost_explorer_data()
    if "Error" in cost_data:
        logger.error("Failed to retrieve cost data")
        return "Error retrieving cost data: " + cost_data["Error"]
    html_report = gen_html_report(cost_data)
    return html_report
