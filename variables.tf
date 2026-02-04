variable "project_name" {
  description = "Name of the project, used for naming the Lambda function and related resources"
  type        = string
  default     = "cw-cost-widget"
}

variable "log_level" {
  description = "Log level for the Lambda function (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL)"
  type        = string
  default     = "INFO"
}

variable "cost_allocation_tag" {
  description = "Cost allocation tag to filter cost data (e.g., 'Environment=Production')"
  type        = string
}
