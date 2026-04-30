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


def _get_lookback_days(event: dict) -> int:
    try:
        days = int(event["widgetContext"]["params"]["lookback_days"])
    except (KeyError, TypeError, ValueError):
        try:
            days = int(os.environ.get("DEFAULT_LOOKBACK_DAYS", 30))
        except (TypeError, ValueError):
            days = 30
    if days <= 0:
        raise ValueError(f"lookback_days must be a positive integer, got {days}")
    return days


def _get_granularity(event: dict) -> str:
    try:
        granularity = str(event["widgetContext"]["params"]["granularity"]).upper()
    except (KeyError, TypeError):
        granularity = os.environ.get("DEFAULT_GRANULARITY", "MONTHLY").upper()
    if granularity not in ("DAILY", "MONTHLY"):
        raise ValueError(f"granularity must be DAILY or MONTHLY, got {granularity!r}")
    return granularity


def _aggregate_results(results_by_time: list) -> tuple[dict[str, float], float]:
    totals: dict[str, float] = {}
    for bucket in results_by_time:
        for g in bucket.get("Groups", []):
            svc = g["Keys"][0]
            cost = float(g["Metrics"]["BlendedCost"]["Amount"])
            totals[svc] = totals.get(svc, 0.0) + cost
    return totals, sum(totals.values())


def _format_period_label(time_period: dict, granularity: str) -> str:
    start = datetime.date.fromisoformat(time_period["Start"])
    if granularity == "MONTHLY":
        return start.strftime("%b %Y")
    return start.strftime("%b %d")


def _fetch_cost(
    start: str,
    end: str,
    tag_key: str,
    tag_values: list[str],
    granularity: str = "MONTHLY",
) -> dict:
    ce = boto3.client("ce", region_name=os.environ.get("AWS_REGION", "us-east-1"))
    try:
        return ce.get_cost_and_usage(
            TimePeriod={"Start": start, "End": end},
            Granularity=granularity,
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


def get_cost_explorer_data(event: dict) -> tuple[dict, str]:
    """Return (cost_data, granularity) from Cost Explorer"""
    tag_key, tag_values = _get_tag_config()
    lookback_days = _get_lookback_days(event)
    granularity = _get_granularity(event)

    today = datetime.date.today()
    delta = datetime.timedelta(days=lookback_days)
    end, start = today, today - delta

    data = _fetch_cost(
        start.isoformat(), end.isoformat(), tag_key, tag_values, granularity
    )

    logger.debug(f"lookback_days={lookback_days} granularity={granularity}")
    logger.debug(f"Period: {start} to {end}")
    return data, granularity


def gen_html_report(data: dict, granularity: str) -> str:
    """Generate styled HTML report with time-series breakdown and service cost summary"""
    results = data["ResultsByTime"]
    period_start = results[0]["TimePeriod"]["Start"]
    period_end = results[-1]["TimePeriod"]["End"]

    totals, grand = _aggregate_results(results)

    services = sorted(
        [(svc, cost) for svc, cost in totals.items() if cost > 0],
        key=lambda x: x[1],
        reverse=True,
    )

    html = (
        "<html><head><style>"
        "body{font-family:Arial,sans-serif;font-size:13px}"
        "h2{margin-bottom:4px}"
        "h3{margin-top:16px;margin-bottom:4px}"
        ".period{color:#666;margin-bottom:12px}"
        "table{border-collapse:collapse;width:100%}"
        "th{background:rgba(128,128,128,0.15);padding:6px 10px;text-align:left;border-bottom:2px solid rgba(128,128,128,0.3)}"
        "th.r,td.r{text-align:right}"
        "td{padding:5px 10px;border-bottom:1px solid rgba(128,128,128,0.15)}"
        "tr:nth-child(even){background:rgba(128,128,128,0.07)}"
        "tr.tot td{font-weight:bold;border-top:2px solid rgba(128,128,128,0.3)}"
        "</style></head><body>"
    )
    html += "<h2>AWS Cost Report</h2>"
    html += f'<div class="period">{period_start} to {period_end}</div>'

    if not services:
        html += "<p>No costs found for the specified tag.</p></body></html>"
        return html

    html += "<h3>Cost Over Time</h3>"
    html += "<table><tr><th>Period</th><th class='r'>Cost (USD)</th></tr>"
    for bucket in results:
        label = _format_period_label(bucket["TimePeriod"], granularity)
        bucket_total = sum(
            float(g["Metrics"]["BlendedCost"]["Amount"])
            for g in bucket.get("Groups", [])
        )
        html += f"<tr><td>{label}</td><td class='r'>${bucket_total:.2f}</td></tr>"
    html += "</table>"

    html += "<h3>Cost by Service</h3>"
    html += "<table><tr><th>Service</th><th class='r'>Cost (USD)</th></tr>"
    for svc, cost in services:
        html += f"<tr><td>{svc}</td><td class='r'>${cost:.2f}</td></tr>"
    html += (
        f"<tr class='tot'><td>Total</td><td class='r'>${grand:.2f}</td></tr>"
        "</table></body></html>"
    )

    logger.debug("Generated HTML report: " + html)
    return html


def lambda_handler(event: dict, context: LambdaContext) -> str:
    """Lambda function handler to generate AWS Cost Report"""
    data, granularity = get_cost_explorer_data(event)
    return gen_html_report(data, granularity)
