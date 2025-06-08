output "lambda_function_name" {
  value = aws_lambda_function.diagram_ai.function_name
}

output "lambda_function_arn" {
  value = aws_lambda_function.diagram_ai.arn
}

output "http_api_endpoint" {
  value = aws_apigatewayv2_api.http_api.api_endpoint
  description = "Invoke URL for the HTTP API Gateway."
}

output "api_endpoint" {
  value = aws_apigatewayv2_stage.default_stage.invoke_url
  description = "Base URL for API Gateway stage."
}

output "curl_example" {
  value = <<EOF
  
Example API usage:

curl -X POST ${aws_apigatewayv2_stage.default_stage.invoke_url}/generate \\
  -H "Authorization: Bearer YOUR_ID_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "description": "AWS web app with EC2 and RDS",
    "provider": "aws"
  }'
EOF
  description = "Example curl command to test the API."
}

# Cognito outputs
output "cognito_user_pool_id" {
  value = var.use_existing_cognito ? var.existing_cognito_user_pool_id : aws_cognito_user_pool.diagram_ai_pool[0].id
  description = "Cognito User Pool ID"
}

output "cognito_user_pool_client_id" {
  value = var.use_existing_cognito ? var.existing_cognito_user_pool_client_id : aws_cognito_user_pool_client.diagram_ai_client[0].id
  description = "Cognito User Pool Client ID"
}

output "cognito_domain" {
  value = var.use_existing_cognito ? "N/A" : "${var.cognito_domain_prefix}.auth.${var.aws_region}.amazoncognito.com"
  description = "Cognito Domain"
}

output "cognito_hosted_ui_url" {
  value = var.use_existing_cognito ? "N/A" : "https://${var.cognito_domain_prefix}.auth.${var.aws_region}.amazoncognito.com/login?client_id=${aws_cognito_user_pool_client.diagram_ai_client[0].id}&response_type=token&scope=email+openid+profile&redirect_uri=${var.cognito_callback_urls[0]}"
  description = "URL for the Cognito Hosted UI"
}
