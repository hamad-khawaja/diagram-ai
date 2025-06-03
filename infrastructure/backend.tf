terraform {
  backend "s3" {
    # Fill in your S3 backend configuration here
    bucket = var.s3_bucket_name
    key    = "terraform.tfstate"
    region = var.aws_region
  }
}
