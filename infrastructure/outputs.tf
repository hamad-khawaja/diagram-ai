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
  -H "Content-Type: application/json" \\
  -d '{
    "description": "AWS web app with EC2 and RDS",
    "provider": "aws"
  }'
EOF
  description = "Example curl command to test the API."
}
