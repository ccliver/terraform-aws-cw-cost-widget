import datetime
import os

import boto3

from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools import Logger
from botocore.exceptions import ClientError

logger = Logger()


def _get_tag_config() -> tuple[str, list[str]]:
    for var in ("COST_ALLOCATION_TAG_KEY", "COST_ALLOCATION_TAG_VALUES"):
        if var not in os.environ:
            raise ValueError(f"{var} environment variable is not set")
    return (
        os.environ["COST_ALLOCATION_TAG_KEY"],
        os.environ["COST_ALLOCATION_TAG_VALUES"].split(","),
    )


def _fetch_cost(start: str, end: str, tag_key: str, tag_values: list[str]) -> dict:
    ce = boto3.client("ce", region_name=os.environ.get("AWS_REGION", "us-east-1"))
    try:
        return ce.get_cost_and_usage(
            TimePeriod={"Start": start, "End": end},
            Granularity="MONTHLY",
            Metrics=["BlendedCost"],
            Filter={
                "Tags": {
                    "Key": tag_key,
                    "Values": tag_values,
                    "MatchOptions": ["EQUALS"],
                }
            },
            GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
        )
    except ClientError as e:
        logger.error(f"Error fetching Cost Explorer data: {e}")
        raise


def get_cost_explorer_data() -> tuple[dict, dict]:
    """Return (current_period_data, prior_period_data) from Cost Explorer"""
    tag_key, tag_values = _get_tag_config()
    show_current_month = os.environ.get("SHOW_CURRENT_MONTH", "false").lower() == "true"

    today = datetime.date.today()
    first = today.replace(day=1)
    last_month_start = (first - datetime.timedelta(days=1)).replace(day=1)

    if show_current_month:
        cur_start, cur_end = first, today
    else:
        cur_start, cur_end = last_month_start, first

    prev_end = cur_start
    prev_start = (cur_start - datetime.timedelta(days=1)).replace(day=1)

    current = _fetch_cost(
        cur_start.isoformat(), cur_end.isoformat(), tag_key, tag_values
    )
    previous = _fetch_cost(
        prev_start.isoformat(), prev_end.isoformat(), tag_key, tag_values
    )

    logger.debug(f"Current period: {current}")
    logger.debug(f"Previous period: {previous}")
    return current, previous


def gen_html_report(current: dict, previous: dict) -> str:
    """Generate styled HTML report with service cost breakdown and MoM delta"""
    period = current["ResultsByTime"][0]["TimePeriod"]
    groups = current["ResultsByTime"][0].get("Groups", [])
    total = sum(float(g["Metrics"]["BlendedCost"]["Amount"]) for g in groups)

    prev_groups = (
        previous["ResultsByTime"][0].get("Groups", [])
        if previous["ResultsByTime"]
        else []
    )
    prev_by_service = {
        g["Keys"][0]: float(g["Metrics"]["BlendedCost"]["Amount"]) for g in prev_groups
    }
    prev_total = sum(float(g["Metrics"]["BlendedCost"]["Amount"]) for g in prev_groups)

    # Filter zero-cost rows and sort by cost descending
    groups = sorted(
        [g for g in groups if float(g["Metrics"]["BlendedCost"]["Amount"]) > 0],
        key=lambda x: float(x["Metrics"]["BlendedCost"]["Amount"]),
        reverse=True,
    )

    html = (
        "<html><head><style>"
        "body{font-family:Arial,sans-serif;font-size:13px}"
        "h2{margin-bottom:4px}"
        ".period{color:#666;margin-bottom:12px}"
        "table{border-collapse:collapse;width:100%}"
        "th{background:rgba(128,128,128,0.15);padding:6px 10px;text-align:left;border-bottom:2px solid rgba(128,128,128,0.3)}"
        "th.r,td.r{text-align:right}"
        "td{padding:5px 10px;border-bottom:1px solid rgba(128,128,128,0.15)}"
        "tr:nth-child(even){background:rgba(128,128,128,0.07)}"
        "tr.tot td{font-weight:bold;border-top:2px solid rgba(128,128,128,0.3)}"
        ".up{color:#d13212}.dn{color:#1d8102}"
        "</style></head><body>"
    )
    html += "<h2>AWS Cost Report</h2>"
    html += f'<div class="period">{period["Start"]} to {period["End"]}</div>'

    if not groups:
        html += "<p>No costs found for the specified tag.</p></body></html>"
        return html

    html += (
        "<table>"
        "<tr><th>Service</th><th class='r'>Cost (USD)</th><th class='r'>vs Prior Month</th></tr>"
    )
    for g in groups:
        svc = g["Keys"][0]
        cost = float(g["Metrics"]["BlendedCost"]["Amount"])
        delta = cost - prev_by_service.get(svc, 0.0)
        sign = "+" if delta >= 0 else ""
        css = "up" if delta > 0 else "dn"
        html += (
            f"<tr><td>{svc}</td><td class='r'>${cost:.2f}</td>"
            f"<td class='r'><span class='{css}'>{sign}{delta:.2f}</span></td></tr>"
        )

    total_delta = total - prev_total
    sign = "+" if total_delta >= 0 else ""
    css = "up" if total_delta > 0 else "dn"
    html += (
        f"<tr class='tot'><td>Total</td><td class='r'>${total:.2f}</td>"
        f"<td class='r'><span class='{css}'>{sign}{total_delta:.2f}</span></td></tr>"
    )
    html += "</table></body></html>"

    logger.debug("Generated HTML report: " + html)
    return html


def lambda_handler(event: dict, context: LambdaContext) -> str:
    """Lambda function handler to generate AWS Cost Report"""
    current, previous = get_cost_explorer_data()
    return gen_html_report(current, previous)
