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

# No new variables needed for API Gateway
