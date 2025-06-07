terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
  required_version = ">= 1.3.0"
  
  backend "s3" {
    bucket = "diagramstf-35956872132"
    key    = "terraform/diagram-ai/terraform.tfstate"
    region = "us-east-1"
    # Uncomment the line below if you have DynamoDB table for state locking
    # dynamodb_table = "terraform-state-lock"
  }
}

provider "aws" {
  region = var.aws_region
}

# HTTP API Gateway
resource "aws_apigatewayv2_api" "http_api" {
  name          = "diagram-ai-http-api"
  protocol_type = "HTTP"
}

# Lambda integration
resource "aws_apigatewayv2_integration" "lambda_integration" {
  api_id                 = aws_apigatewayv2_api.http_api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.diagram_ai.invoke_arn
  integration_method     = "POST"
  payload_format_version = "2.0"
}

# Route for ANY /{proxy+}
resource "aws_apigatewayv2_route" "default_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "$default"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
  
  # By default, require authentication for all endpoints
  # Specific public routes are defined separately
  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.cognito_authorizer.id
}

# API Gateway stage
resource "aws_apigatewayv2_stage" "default_stage" {
  api_id      = aws_apigatewayv2_api.http_api.id
  name        = "$default"
  auto_deploy = true
}

# Lambda permission for API Gateway
resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.diagram_ai.arn
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*"
}
