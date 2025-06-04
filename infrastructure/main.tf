# Allow EC2 to upload and get objects from the S3 uploads bucket
resource "aws_iam_role_policy" "ec2_s3_upload" {
  name = "ec2-s3-upload"
  role = aws_iam_role.diagrams_ec2_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject"
        ]
        Resource = "${aws_s3_bucket.uploads.arn}/*"
      }
    ]
  })
}
# SSM Parameter Store for LLM provider
resource "aws_ssm_parameter" "llm_provider" {
  name  = "/diagram-ai/llm_provider"
  type  = "String"
  value = "openai"
}
# SSM Parameter Store for S3 bucket name
resource "aws_ssm_parameter" "s3_bucket" {
  name  = "/diagram-ai/s3_bucket"
  type  = "String"
  value = aws_s3_bucket.uploads.bucket
}
# Attach ECR read-only policy to EC2 role for pulling images
resource "aws_iam_role_policy_attachment" "ecr_readonly" {
  role       = aws_iam_role.diagrams_ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}
# Attach AmazonSSMManagedInstanceCore policy to the EC2 role
resource "aws_iam_role_policy_attachment" "ssm_core" {
  role       = aws_iam_role.diagrams_ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}
# Security group to allow HTTPS (443) and app port (5050) inbound
resource "aws_security_group" "diagrams_https" {
  name        = "diagrams-https-sg"
  description = "Allow HTTPS and app port inbound"
  vpc_id      = aws_vpc.diagrams_vpc.id

  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "App port"
    from_port   = 5050
    to_port     = 5050
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "diagrams-https-sg"
  }
}
# --- HTTP API Gateway for Flask EC2 ---
resource "aws_apigatewayv2_api" "diagram_http_api" {
  name          = "diagram-http-api"
  protocol_type = "HTTP"
  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["POST", "OPTIONS"]
    allow_headers = ["content-type"]
    max_age = 86400
  }
}

# Get the public IP of the EC2 instance
data "aws_instance" "diagram_ec2" {
  instance_id = aws_instance.diagram_ec2.id
}

# Integration: Forward to EC2 public endpoint
resource "aws_apigatewayv2_integration" "diagram_ec2_integration" {
  api_id           = aws_apigatewayv2_api.diagram_http_api.id
  integration_type = "HTTP_PROXY"
  integration_method = "ANY"
  integration_uri  = "http://${data.aws_instance.diagram_ec2.public_ip}:5050/{proxy}"
  request_parameters = {
    "overwrite:path" = "$request.path"
  }
}

# /generate route

# Catch-all proxy route for all paths and methods
resource "aws_apigatewayv2_route" "proxy" {
  api_id    = aws_apigatewayv2_api.diagram_http_api.id
  route_key = "ANY /{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.diagram_ec2_integration.id}"
}

# Default stage (auto-deploy)
resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.diagram_http_api.id
  name        = "$default"
  auto_deploy = true
  # No CORS or access log settings here; CORS is set per route for HTTP API
}

output "http_api_endpoint" {
  value = aws_apigatewayv2_api.diagram_http_api.api_endpoint
}
# Create a new VPC
resource "aws_vpc" "diagrams_vpc" {
  cidr_block = "10.0.0.0/28" # 16 IPs, 11 usable
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = {
    Name = "diagrams-vpc"
  }
}

# Create a public subnet in the VPC
resource "aws_subnet" "diagrams_public_subnet" {
  vpc_id                  = aws_vpc.diagrams_vpc.id
  cidr_block              = "10.0.0.0/28" # 16 IPs, 11 usable
  map_public_ip_on_launch = true
  availability_zone       = "us-east-1a"
  tags = {
    Name = "diagrams-public-subnet"
  }
}

# Create an internet gateway for the VPC
resource "aws_internet_gateway" "diagrams_igw" {
  vpc_id = aws_vpc.diagrams_vpc.id
  tags = {
    Name = "diagrams-igw"
  }
}

# Create a route table for the public subnet
resource "aws_route_table" "diagrams_public_rt" {
  vpc_id = aws_vpc.diagrams_vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.diagrams_igw.id
  }
  tags = {
    Name = "diagrams-public-rt"
  }
}

# Associate the route table with the public subnet
resource "aws_route_table_association" "diagrams_public_assoc" {
  subnet_id      = aws_subnet.diagrams_public_subnet.id
  route_table_id = aws_route_table.diagrams_public_rt.id
}
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


resource "aws_instance" "diagram_ec2" {
  ami           = "ami-0c94855ba95c71c99" # Amazon Linux 2 AMI (example, update as needed)
  instance_type = "t2.micro"
  subnet_id     = aws_subnet.diagrams_public_subnet.id
  vpc_security_group_ids = [aws_security_group.diagrams_https.id]
  iam_instance_profile = aws_iam_instance_profile.diagrams_ec2_profile.name
  tags = {
    Name = "diagram-ec2"
  }
  user_data = <<-EOF
    #!/bin/bash
    sudo yum update -y
    sudo amazon-linux-extras install docker -y
    sudo systemctl enable docker
    sudo systemctl start docker
    sleep 10

    # Authenticate Docker to ECR (modern method)
    aws ecr get-login-password --region us-east-1 | sudo docker login --username AWS --password-stdin 016683085931.dkr.ecr.us-east-1.amazonaws.com

    # Fetch secrets from SSM Parameter Store
    OPENAI_API_KEY=$(aws ssm get-parameter --region us-east-1 --name "/diagram-ai/openai_api_key" --with-decryption --query "Parameter.Value" --output text)
    S3_BUCKET=$(aws ssm get-parameter --region us-east-1 --name "/diagram-ai/s3_bucket" --query "Parameter.Value" --output text)
    LLM_PROVIDER=$(aws ssm get-parameter --region us-east-1 --name "/diagram-ai/llm_provider" --query "Parameter.Value" --output text)

    # Pull and run your image with env vars
    sudo docker pull 016683085931.dkr.ecr.us-east-1.amazonaws.com/diagrams:latest
    sudo docker run -d \
      -p 5050:5050 \
      -e OPENAI_API_KEY="$OPENAI_API_KEY" \
      -e S3_BUCKET="$S3_BUCKET" \
      -e LLM_PROVIDER="$LLM_PROVIDER" \
      016683085931.dkr.ecr.us-east-1.amazonaws.com/diagrams:latest
  EOF
}
resource "aws_iam_instance_profile" "diagrams_ec2_profile" {
  name = "diagrams-ec2"
  role = aws_iam_role.diagrams_ec2_role.name
}

resource "aws_iam_role" "diagrams_ec2_role" {
  name = "diagrams-ec2"
  assume_role_policy = data.aws_iam_policy_document.ec2_assume_role_policy.json
}

data "aws_iam_policy_document" "ec2_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}