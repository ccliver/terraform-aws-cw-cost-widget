provider "aws" {
  region = "us-east-1"
}

module "example" {
  source                     = "../../"
  cost_allocation_tag_key    = "Project"
  cost_allocation_tag_values = ["k8s-lab"]
}

resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "terraform-aws-cw-cost-widget"

  dashboard_body = templatefile(
    "./dashboard.tftpl",
    { widget_arn = module.example.lambda_function_arn }
  )
}
