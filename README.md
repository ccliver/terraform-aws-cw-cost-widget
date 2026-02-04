# CloudWatch custom widget Lambda to display cost on dashboards

[![CI](https://github.com/ccliver/terraform-aws-cw-cost-widget/actions/workflows/ci.yml/badge.svg)](https://github.com/ccliver/terraform-aws-cw-cost-widget/actions/workflows/ci.yml)

![Alt CloudWatch Custom Widget](widget.png)

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
| <a name="input_cost_allocation_tag"></a> [cost\_allocation\_tag](#input\_cost\_allocation\_tag) | Cost allocation tag to filter cost data (e.g., 'Environment=Production') | `string` | n/a | yes |
| <a name="input_log_level"></a> [log\_level](#input\_log\_level) | Log level for the Lambda function (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL) | `string` | `"INFO"` | no |
| <a name="input_project_name"></a> [project\_name](#input\_project\_name) | Name of the project, used for naming the Lambda function and related resources | `string` | `"cw-cost-widget"` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_arn"></a> [arn](#output\_arn) | The ARN of the CloudWatch custom widget Lambda function |
<!-- END_TF_DOCS -->
