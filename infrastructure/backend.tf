terraform {
  backend "s3" {
    # Fill in your S3 backend configuration here
    bucket = "diagramstf-35956872132"
    key    = "terraform.tfstate"
    region = "us-east-1"
  }
}
