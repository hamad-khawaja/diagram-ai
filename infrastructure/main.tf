# Terraform configuration for diagram-ai infrastructure

resource "aws_s3_bucket" "uploads" {
  bucket = var.s3_bucket_name_uploads
  force_destroy = true
}

output "uploads_bucket_name" {
  value = aws_s3_bucket.uploads.bucket
}
output "uploads_bucket_arn" {
  value = aws_s3_bucket.uploads.arn
}
