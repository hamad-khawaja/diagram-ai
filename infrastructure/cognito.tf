locals {
  # Use existing Cognito resources or create new ones
  user_pool_id = var.use_existing_cognito ? var.existing_cognito_user_pool_id : aws_cognito_user_pool.diagram_ai_pool[0].id
  client_id = var.use_existing_cognito ? var.existing_cognito_user_pool_client_id : aws_cognito_user_pool_client.diagram_ai_client[0].id
  issuer_url = "https://cognito-idp.${var.aws_region}.amazonaws.com/${local.user_pool_id}"
}

# Create new Cognito User Pool only if not using existing one
resource "aws_cognito_user_pool" "diagram_ai_pool" {
  count = var.use_existing_cognito ? 0 : 1
  
  name = "diagram-ai-user-pool"
  
  # Password policy
  password_policy {
    minimum_length    = 8
    require_lowercase = true
    require_numbers   = true
    require_symbols   = true
    require_uppercase = true
  }
  
  # MFA configuration
  mfa_configuration = "OFF"
  
  # Verification settings
  email_configuration {
    email_sending_account = "COGNITO_DEFAULT"
  }
  
  username_attributes = ["email"]
  
  # Schema attributes
  schema {
    name                     = "email"
    attribute_data_type      = "String"
    developer_only_attribute = false
    mutable                  = true
    required                 = true
  }
  
  tags = {
    Name = "DiagramAI User Pool"
  }
}

# Create new User Pool Client only if not using existing one
resource "aws_cognito_user_pool_client" "diagram_ai_client" {
  count = var.use_existing_cognito ? 0 : 1
  
  name                = "diagram-ai-client"
  user_pool_id        = aws_cognito_user_pool.diagram_ai_pool[0].id
  
  # No client secret for public clients (e.g., web apps)
  generate_secret     = false
  
  # Token validity
  refresh_token_validity = 30
  access_token_validity  = 1
  id_token_validity      = 1
  token_validity_units {
    access_token  = "hours"
    id_token      = "hours"
    refresh_token = "days"
  }
  
  # OAuth settings
  allowed_oauth_flows  = ["implicit", "code"]
  allowed_oauth_scopes = ["email", "openid", "profile"]
  callback_urls        = var.cognito_callback_urls
  logout_urls          = var.cognito_logout_urls
  supported_identity_providers = ["COGNITO"]
  
  # Use Cognito's hosted UI
  explicit_auth_flows = [
    "ALLOW_USER_SRP_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH",
    "ALLOW_USER_PASSWORD_AUTH"
  ]
}

# Optional: Create a domain for the Cognito hosted UI (only if not using existing)
resource "aws_cognito_user_pool_domain" "diagram_ai_domain" {
  count = var.use_existing_cognito ? 0 : 1
  
  domain       = var.cognito_domain_prefix
  user_pool_id = aws_cognito_user_pool.diagram_ai_pool[0].id
}

# Create JWT authorizer for API Gateway using either existing or new Cognito
resource "aws_apigatewayv2_authorizer" "cognito_authorizer" {
  api_id           = aws_apigatewayv2_api.http_api.id
  authorizer_type  = "JWT"
  identity_sources = ["$request.header.Authorization"]
  name             = "diagram-ai-cognito-authorizer"
  
  jwt_configuration {
    audience = [local.client_id]
    issuer   = local.issuer_url
  }
}

# Protected route example - replace the default route
resource "aws_apigatewayv2_route" "protected_generate_route" {
  api_id             = aws_apigatewayv2_api.http_api.id
  route_key          = "POST /generate"
  target             = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.cognito_authorizer.id
}

# Public health check route (no auth required)
resource "aws_apigatewayv2_route" "health_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "GET /health"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}
