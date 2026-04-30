data "aws_iam_policy_document" "lambda_execution" {
  statement {
    actions   = ["ce:GetCostAndUsage"]
    resources = ["*"]
  }
}

module "widget" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "8.5.0"

  function_name                 = var.project_name
  description                   = "Custom widget to display AWS cost data in CloudWatch dashboards"
  handler                       = "src.cost_widget.main.lambda_handler"
  runtime                       = "python3.13"
  logging_application_log_level = var.log_level
  attach_policy_jsons           = true
  number_of_policy_jsons        = 1
  policy_jsons                  = [data.aws_iam_policy_document.lambda_execution.json]

  ignore_source_code_hash = true

  source_path = [
    {
      path       = "${path.module}/cost_widget/"
      uv_install = true
      patterns = [
        "!tests/.*",
        "!.venv/.*",
        "!uv.lock",
        "!pyproject.toml",
        "!README.md",
      ]
    }
  ]

  environment_variables = {
    POWERTOOLS_LOG_LEVEL       = var.log_level
    COST_ALLOCATION_TAG_KEY    = var.cost_allocation_tag_key
    COST_ALLOCATION_TAG_VALUES = join(",", var.cost_allocation_tag_values)
    DEFAULT_LOOKBACK_DAYS      = tostring(var.default_lookback_days)
    DEFAULT_GRANULARITY        = var.default_granularity
  }

  tags = merge(
    { Name = var.project_name },
    var.tags,
  )
}
