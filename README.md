# CloudWatch custom widget Lambda to display cost on dashboards

[![CI](https://github.com/ccliver/terraform-aws-cw-cost-widget/actions/workflows/ci.yml/badge.svg)](https://github.com/ccliver/terraform-aws-cw-cost-widget/actions/workflows/ci.yml)

![Alt CloudWatch Custom Widget](widget.png)

## Configuring the widget

The lookback window and granularity can be changed at runtime by editing the widget's `params` JSON in the CloudWatch dashboard — no Terraform redeployment needed.

In the CloudWatch console, open the dashboard, click the widget's action menu (⋮) → **Edit**, then update the **Parameters** field:

```json
{
  "lookback_days": 30,
  "granularity": "MONTHLY"
}
```

| Parameter | Description | Example values |
|-----------|-------------|----------------|
| `lookback_days` | Number of days to look back from today | `1`, `7`, `30`, `90` (any positive integer) |
| `granularity` | How Cost Explorer buckets the data | `"DAILY"`, `"MONTHLY"` |

With `DAILY` granularity the **Cost Over Time** table shows one row per day; with `MONTHLY` it shows one row per calendar month. The defaults can also be set permanently via the `default_lookback_days` and `default_granularity` Terraform variables.

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.0 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | ~> 6 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | ~> 6 |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_widget"></a> [widget](#module\_widget) | terraform-aws-modules/lambda/aws | 8.5.0 |

## Resources

| Name | Type |
|------|------|
| [aws_iam_policy_document.lambda_execution](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_cost_allocation_tag_key"></a> [cost\_allocation\_tag\_key](#input\_cost\_allocation\_tag\_key) | Cost allocation tag key to filter cost data (e.g., 'Environment') | `string` | n/a | yes |
| <a name="input_cost_allocation_tag_values"></a> [cost\_allocation\_tag\_values](#input\_cost\_allocation\_tag\_values) | List of cost allocation tag values to filter cost data (e.g., ['Production', 'Staging']) | `list(string)` | n/a | yes |
| <a name="input_default_granularity"></a> [default\_granularity](#input\_default\_granularity) | Default Cost Explorer granularity (DAILY or MONTHLY). Override at runtime via widget params without redeploying. | `string` | `"MONTHLY"` | no |
| <a name="input_default_lookback_days"></a> [default\_lookback\_days](#input\_default\_lookback\_days) | Default lookback window in days (any positive integer). Override at runtime via widget params without redeploying. | `number` | `30` | no |
| <a name="input_log_level"></a> [log\_level](#input\_log\_level) | Log level for the Lambda function (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL) | `string` | `"INFO"` | no |
| <a name="input_project_name"></a> [project\_name](#input\_project\_name) | Name of the project, used for naming the Lambda function and related resources | `string` | `"cw-cost-widget"` | no |
| <a name="input_tags"></a> [tags](#input\_tags) | Tags to apply to all resources | `map(string)` | `{}` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_lambda_cloudwatch_log_group_name"></a> [lambda\_cloudwatch\_log\_group\_name](#output\_lambda\_cloudwatch\_log\_group\_name) | The name of the CloudWatch log group for the Lambda function |
| <a name="output_lambda_function_arn"></a> [lambda\_function\_arn](#output\_lambda\_function\_arn) | The ARN of the CloudWatch custom widget Lambda function |
| <a name="output_lambda_function_name"></a> [lambda\_function\_name](#output\_lambda\_function\_name) | The name of the CloudWatch custom widget Lambda function |
| <a name="output_lambda_role_arn"></a> [lambda\_role\_arn](#output\_lambda\_role\_arn) | The ARN of the IAM role attached to the Lambda function |
<!-- END_TF_DOCS -->
