import os
import pytest
import boto3
import requests
from moto import mock_aws

os.environ["COST_ALLOCATION_TAG_KEY"] = "Project"
os.environ["COST_ALLOCATION_TAG_VALUES"] = "Testing"
os.environ["DEFAULT_LOOKBACK_DAYS"] = "30"
os.environ["DEFAULT_GRANULARITY"] = "MONTHLY"


@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


@pytest.fixture(scope="function")
def ce(aws_credentials):
    """
    Return a mocked Cost Explorer client
    """
    with mock_aws():
        yield boto3.client("ce", region_name="us-east-1")


@pytest.fixture(scope="function")
def setup_ce(ce):
    """Setup mocked Cost Explorer data"""

    expected_results = {
        "results": [
            {
                "ResultsByTime": [
                    {
                        "Estimated": False,
                        "Groups": [
                            {
                                "Keys": ["AWS Key Management Service"],
                                "Metrics": {
                                    "BlendedCost": {
                                        "Amount": "0.016129032",
                                        "Unit": "USD",
                                    }
                                },
                            },
                            {
                                "Keys": ["EC2 - Other"],
                                "Metrics": {
                                    "BlendedCost": {
                                        "Amount": "2.1637555078",
                                        "Unit": "USD",
                                    }
                                },
                            },
                            {
                                "Keys": ["Amazon Elastic Compute Cloud - Compute"],
                                "Metrics": {
                                    "BlendedCost": {
                                        "Amount": "0.1253604212",
                                        "Unit": "USD",
                                    }
                                },
                            },
                            {
                                "Keys": [
                                    "Amazon Elastic Container Service for Kubernetes"
                                ],
                                "Metrics": {
                                    "BlendedCost": {
                                        "Amount": "0.93173986",
                                        "Unit": "USD",
                                    }
                                },
                            },
                            {
                                "Keys": ["Amazon Simple Storage Service"],
                                "Metrics": {
                                    "BlendedCost": {
                                        "Amount": "0.0013050106",
                                        "Unit": "USD",
                                    }
                                },
                            },
                            {
                                "Keys": ["Amazon Virtual Private Cloud"],
                                "Metrics": {
                                    "BlendedCost": {
                                        "Amount": "0.009947235",
                                        "Unit": "USD",
                                    }
                                },
                            },
                            {
                                "Keys": ["AmazonCloudWatch"],
                                "Metrics": {
                                    "BlendedCost": {"Amount": "0", "Unit": "USD"}
                                },
                            },
                        ],
                        "TimePeriod": {"End": "2026-02-01", "Start": "2026-01-01"},
                        "Total": {},
                    }
                ],
                "DimensionValueAttributes": [],
            }
        ]
    }

    # Each get_cost_explorer_data() call makes 1 CE request.
    # Post 2 results to the queue to cover up to 2 test calls per fixture scope.
    for _ in range(2):
        resp = requests.post(
            "http://motoapi.amazonaws.com/moto-api/static/ce/cost-and-usage-results",
            json=expected_results,
        )
        assert resp.status_code == 201
