variable "aws_region" {
  description = "AWS region to deploy resources."
  type        = string
  default     = "us-east-1"
}

variable "lambda_image_uri" {
  description = "ECR image URI for the Lambda container."
  type        = string
}

variable "lambda_function_name" {
  description = "Name for the Lambda function."
  type        = string
  default     = "diagram-ai-lambda"
}

variable "s3_bucket" {
  description = "S3 bucket name for diagram outputs."
  type        = string
}

variable "ecr_repository_name" {
  description = "ECR repository name for the Lambda container image."
  type        = string
}

variable "openai_api_key" {
  description = "OpenAI API key for generating diagrams."
  type        = string
  sensitive   = true  # Mark as sensitive to prevent it from showing in logs
}

# Cognito variables
variable "cognito_callback_urls" {
  description = "Callback URLs for the Cognito user pool client"
  type        = list(string)
  default     = ["https://example.com/callback"]
}

variable "cognito_logout_urls" {
  description = "Logout URLs for the Cognito user pool client"
  type        = list(string)
  default     = ["https://example.com/logout"]
}

variable "cognito_domain_prefix" {
  description = "Domain prefix for the Cognito hosted UI"
  type        = string
  default     = "diagram-ai"
}

variable "use_existing_cognito" {
  description = "Set to true to use an existing Cognito User Pool"
  type        = bool
  default     = false
}

variable "existing_cognito_user_pool_id" {
  description = "ID of an existing Cognito User Pool (if use_existing_cognito is true)"
  type        = string
  default     = ""
}

variable "existing_cognito_user_pool_client_id" {
  description = "ID of an existing Cognito User Pool Client (if use_existing_cognito is true)"
  type        = string
  default     = ""
}
