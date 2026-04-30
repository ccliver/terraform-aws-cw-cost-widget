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

variable "default_lookback_days" {
  description = "Default lookback window in days (any positive integer). Override at runtime via widget params without redeploying."
  type        = number
  default     = 30

  validation {
    condition     = var.default_lookback_days > 0
    error_message = "default_lookback_days must be a positive integer."
  }
}

variable "default_granularity" {
  description = "Default Cost Explorer granularity (DAILY or MONTHLY). Override at runtime via widget params without redeploying."
  type        = string
  default     = "MONTHLY"

  validation {
    condition     = contains(["DAILY", "MONTHLY"], var.default_granularity)
    error_message = "default_granularity must be DAILY or MONTHLY."
  }
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default     = {}
}
