variable "aws_region" {
  description = "AWS region to deploy resources in."
  type        = string
  default     = "us-east-1"
}

variable "s3_bucket_name_uploads" {
  description = "Name of the S3 bucket for storing uploaded diagrams."
  type        = string
}