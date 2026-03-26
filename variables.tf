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

variable "cost_allocation_tag_key" {
  description = "Cost allocation tag key to filter cost data (e.g., 'Environment')"
  type        = string
}

variable "cost_allocation_tag_values" {
  description = "List of cost allocation tag values to filter cost data (e.g., ['Production', 'Staging'])"
  type        = list(string)
}

variable "show_current_month" {
  description = "Show current month MTD costs instead of the last complete month"
  type        = bool
  default     = false
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default     = {}
}
