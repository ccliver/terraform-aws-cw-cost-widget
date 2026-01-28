provider "aws" {
  region = "us-east-1"
}

module "{{module_name}}" {
  source = "../../"
}
