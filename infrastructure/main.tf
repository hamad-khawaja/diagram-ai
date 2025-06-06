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

# --- Cognito User Pool ---
resource "aws_cognito_user_pool" "diagram_users" {
  name = "diagram-users"
}

# --- Cognito User Pool Domain ---
resource "aws_cognito_user_pool_domain" "diagram_users_domain" {
  domain       = "diagram-users-${random_id.suffix.hex}"
  user_pool_id = aws_cognito_user_pool.diagram_users.id
}

# --- Cognito User Pool Client ---
resource "aws_cognito_user_pool_client" "diagram_users_client" {
  name         = "diagram-users-client"
  user_pool_id = aws_cognito_user_pool.diagram_users.id
  generate_secret = false
  allowed_oauth_flows = ["code", "implicit"]
  allowed_oauth_scopes = ["openid", "email", "profile"]
  allowed_oauth_flows_user_pool_client = true
  callback_urls = ["https://diagram-web-ai.vercel.app/callback"] # <-- update this
  logout_urls   = ["https://diagram-web-ai.vercel.app/logout"]  # <-- update this
  supported_identity_providers = ["COGNITO"]
}

resource "random_id" "suffix" {
  byte_length = 4
}

# --- API Gateway JWT Authorizer ---
resource "aws_apigatewayv2_authorizer" "diagram_jwt_auth" {
  api_id           = aws_apigatewayv2_api.diagram_http_api.id
  authorizer_type  = "JWT"
  identity_sources = ["$request.header.Authorization"]
  name             = "diagram-jwt-auth"
  jwt_configuration {
    audience = [aws_cognito_user_pool_client.diagram_users_client.id]
    issuer   = "https://cognito-idp.us-east-1.amazonaws.com/${aws_cognito_user_pool.diagram_users.id}"
  }
}


# CloudWatch Log Group for API Gateway access logs
resource "aws_cloudwatch_log_group" "apigw_access_logs" {
  name              = "/aws/apigateway/diagram-http-api"
  retention_in_days = 14
}

# Default stage (auto-deploy)
resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.diagram_http_api.id
  name        = "$default"
  auto_deploy = true
  default_route_settings {
    throttling_burst_limit = 100
    throttling_rate_limit  = 50
  }
  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.apigw_access_logs.arn
    format = jsonencode({
      requestId               = "$context.requestId"
      ip                      = "$context.identity.sourceIp"
      requestTime             = "$context.requestTime"
      httpMethod              = "$context.httpMethod"
      routeKey                = "$context.routeKey"
      status                  = "$context.status"
      protocol                = "$context.protocol"
      responseLength          = "$context.responseLength"
      integrationErrorMessage = "$context.integrationErrorMessage"
    })
  }
  # No CORS settings here; CORS is set per route for HTTP API
}

output "http_api_endpoint" {
  value = aws_apigatewayv2_api.diagram_http_api.api_endpoint
}
# Create a new VPC
resource "aws_vpc" "diagrams_vpc" {
  cidr_block = "10.0.0.0/16" # 65,536 IPs
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = {
    Name = "diagrams-vpc"
  }
}

# Create a public subnet in the VPC (AZ a)
resource "aws_subnet" "diagrams_public_subnet" {
  vpc_id                  = aws_vpc.diagrams_vpc.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true
  availability_zone       = data.aws_availability_zones.available.names[0]
  tags = {
    Name = "diagrams-public-subnet-a"
  }
}

# Create a second public subnet in the VPC (AZ b)
resource "aws_subnet" "diagrams_public_subnet_b" {
  vpc_id                  = aws_vpc.diagrams_vpc.id
  cidr_block              = "10.0.2.0/24"
  map_public_ip_on_launch = true
  availability_zone       = data.aws_availability_zones.available.names[1]
  tags = {
    Name = "diagrams-public-subnet-b"
  }
}

# --- Data source for AZs (if not already present) ---
data "aws_availability_zones" "available" {}

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


# --- Launch Template for Auto Scaling Group ---
resource "aws_launch_template" "diagram_lt" {
  name_prefix   = "diagram-lt-"
  image_id      = "ami-0c94855ba95c71c99" # Amazon Linux 2 AMI (update as needed)
  instance_type = "t2.micro"
  iam_instance_profile {
    name = aws_iam_instance_profile.diagrams_ec2_profile.name
  }
  vpc_security_group_ids = [aws_security_group.diagrams_https.id]
  user_data = base64encode(<<-EOF
    #!/bin/bash
    set -euxo pipefail
    exec > /var/log/user-data.log 2>&1

    yum update -y
    amazon-linux-extras install docker -y
    systemctl enable docker
    systemctl start docker
    usermod -a -G docker ec2-user

    # Wait for Docker to be up
    for i in {1..10}; do
      if systemctl is-active --quiet docker; then
        echo "Docker is running."
        break
      fi
      echo "Waiting for Docker to start... ($i)"
      sleep 3
    done

    # Authenticate Docker to ECR (modern method)
    if ! aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 016683085931.dkr.ecr.us-east-1.amazonaws.com; then
      echo "[WARN] Docker ECR login failed, continuing anyway."
    fi

    # Fetch secrets from SSM Parameter Store
    export OPENAI_API_KEY=$(aws ssm get-parameter --region us-east-1 --name "/diagram-ai/openai_api_key" --with-decryption --query "Parameter.Value" --output text || true)
    export S3_BUCKET=$(aws ssm get-parameter --region us-east-1 --name "/diagram-ai/s3_bucket" --query "Parameter.Value" --output text || true)
    export LLM_PROVIDER=$(aws ssm get-parameter --region us-east-1 --name "/diagram-ai/llm_provider" --query "Parameter.Value" --output text || true)

    # Pull and run your image with env vars (do not fail if pull/run fails)
    docker pull 016683085931.dkr.ecr.us-east-1.amazonaws.com/diagrams:latest || echo "[WARN] Docker image pull failed, container will not start."
    docker run -d \
      -p 5050:5050 \
      -e OPENAI_API_KEY="$OPENAI_API_KEY" \
      -e S3_BUCKET="$S3_BUCKET" \
      -e LLM_PROVIDER="$LLM_PROVIDER" \
      016683085931.dkr.ecr.us-east-1.amazonaws.com/diagrams:latest || echo "[WARN] Docker run failed."
  EOF
  )
  tag_specifications {
    resource_type = "instance"
    tags = {
      Name = "diagram-ec2"
    }
  }
}

# --- Auto Scaling Group ---
resource "aws_autoscaling_group" "diagram_asg" {
  name                      = "diagram-asg"
  max_size                  = 1
  min_size                  = 1
  desired_capacity          = 1
  vpc_zone_identifier       = [aws_subnet.diagrams_public_subnet.id, aws_subnet.diagrams_public_subnet_b.id]
  launch_template {
    id      = aws_launch_template.diagram_lt.id
    version = "$Latest"
  }
  target_group_arns         = [aws_lb_target_group.diagram_tg.arn]
  health_check_type         = "EC2"
  health_check_grace_period = 60
  tag {
    key                 = "Name"
    value               = "diagram-ec2"
    propagate_at_launch = true
  }
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

# --- ALB Security Group ---
resource "aws_security_group" "alb_sg" {
  name        = "diagram-alb-sg"
  description = "Allow HTTP/HTTPS to ALB"
  vpc_id      = aws_vpc.diagrams_vpc.id

  ingress {
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
}

# --- Application Load Balancer ---
resource "aws_lb" "diagram_alb" {
  name               = "diagram-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = [aws_subnet.diagrams_public_subnet.id, aws_subnet.diagrams_public_subnet_b.id]
}

# --- Target Group for ASG ---
resource "aws_lb_target_group" "diagram_tg" {
  name     = "diagram-tg"
  port     = 5050
  protocol = "HTTP"
  vpc_id   = aws_vpc.diagrams_vpc.id
  health_check {
    path                = "/"
    protocol            = "HTTP"
    matcher             = "200-499"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }
}

# --- ALB Listener ---
resource "aws_lb_listener" "diagram_listener" {
  load_balancer_arn = aws_lb.diagram_alb.arn
  port              = 5050
  protocol          = "HTTP"
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.diagram_tg.arn
  }
}

# --- API Gateway Integration for ALB ---
resource "aws_apigatewayv2_integration" "alb_integration" {
  api_id              = aws_apigatewayv2_api.diagram_http_api.id
  integration_type    = "HTTP_PROXY"
  integration_method  = "ANY"
  integration_uri     = "http://${aws_lb.diagram_alb.dns_name}:5050/{proxy}"
}

# --- API Gateway Route for ALB ---
resource "aws_apigatewayv2_route" "proxy" {
  api_id    = aws_apigatewayv2_api.diagram_http_api.id
  route_key = "ANY /{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.alb_integration.id}"
  authorizer_id = aws_apigatewayv2_authorizer.diagram_jwt_auth.id
  authorization_type = "JWT"
}