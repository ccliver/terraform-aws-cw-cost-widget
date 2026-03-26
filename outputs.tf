output "lambda_function_arn" {
  description = "The ARN of the CloudWatch custom widget Lambda function"
  value       = module.widget.lambda_function_arn
}

output "lambda_function_name" {
  description = "The name of the CloudWatch custom widget Lambda function"
  value       = module.widget.lambda_function_name
}

output "lambda_role_arn" {
  description = "The ARN of the IAM role attached to the Lambda function"
  value       = module.widget.lambda_role_arn
}

output "lambda_cloudwatch_log_group_name" {
  description = "The name of the CloudWatch log group for the Lambda function"
  value       = module.widget.lambda_cloudwatch_log_group_name
}
