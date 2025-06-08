resource "aws_lambda_function" "diagram_ai" {
  function_name = var.lambda_function_name
  package_type  = "Image"
  image_uri     = var.lambda_image_uri
  role          = aws_iam_role.lambda_exec.arn
  timeout       = 900
  memory_size   = 2048
  
  # Explicitly set architecture to x86_64 to match the Docker build
  architectures = ["x86_64"]
  
  environment {
    variables = {
      S3_BUCKET    = var.s3_bucket
      LLM_PROVIDER = "openai" # or set as needed
      OPENAI_API_KEY = var.openai_api_key
    }
  }
}

resource "aws_iam_role" "lambda_exec" {
  name = "diagram-ai-lambda-exec"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "lambda_s3" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

# Allow Lambda to pull images from ECR
resource "aws_iam_role_policy_attachment" "lambda_ecr" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}
