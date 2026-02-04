output "arn" {
  description = "The ARN of the CloudWatch custom widget Lambda function"
  value       = module.widget.lambda_function_arn
}
