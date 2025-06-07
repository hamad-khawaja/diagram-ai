# Lambda Function Troubleshooting Guide

## Common Issues and Solutions

### Lambda Container Image Error

If you're getting an error like:
```
Error: updating Lambda Function (diagram-ai-lambda) code: operation error Lambda: UpdateFunctionCode, https response error StatusCode: 400, RequestID: xxxx, InvalidParameterValueException: The image manifest, config or layer media type for the source image xxx.dkr.ecr.xxx.amazonaws.com/diagram-ai:latest is not supported.
```

This means there's an issue with the Docker image format for Lambda. To fix this:

1. **Use the provided build script**:
   ```bash
   ./build_lambda_image.sh
   ```
   This script ensures the Docker image is built with the correct platform (linux/amd64) and properly pushed to ECR.

2. **Apply Terraform changes**:
   ```bash
   cd infrastructure
   terraform apply
   ```

### 500 Internal Server Error

### 500 Internal Server Error

If you're getting a 500 Internal Server Error when calling your API, follow these steps:

1. **Check CloudWatch Logs**: 
   ```bash
   aws logs get-log-events --log-group-name /aws/lambda/diagram-ai-lambda --log-stream-name "$(aws logs describe-log-streams --log-group-name /aws/lambda/diagram-ai-lambda --order-by LastEventTime --descending --limit 1 --query 'logStreams[0].logStreamName' --output text)"
   ```

2. **Verify OpenAI API Key**:
   - Ensure your OpenAI API key is valid and has access to the gpt-4o model
   - Make sure the key is correctly set in the Lambda environment variables

3. **Fix OpenAI Model Issues**:
   If your logs show an error related to the model, you may need to update the model name:
   ```bash
   # Update the model in llm_providers.py
   sed -i '' "s|model=\"gpt-4.1\"|model=\"gpt-4o\"|g" llm_providers.py
   
   # Then redeploy
   ./deploy.sh YOUR_OPENAI_API_KEY
   ```

4. **Read-Only File System Error**:
   If you see an error like `OSError: [Errno 30] Read-only file system: 'diagrams/...'`, this is because Lambda functions can only write to the `/tmp` directory:
   
   This error occurs when the Lambda function tries to write to a location outside of `/tmp`. AWS Lambda only allows writing to the `/tmp` directory.
   
   The error can appear in various forms:
   ```
   OSError: [Errno 30] Read-only file system: 'diagrams/aws-47b3b493-072e-42ea-a0af-50a6cf0c77b2'
   ```
   or
   ```
   OSError: [Errno 30] Read-only file system: 'diagrams/aws-5b5fd755-0a1f-402a-afff-4a0508480552'
   ```
   or
   ```
   File "/var/lang/lib/python3.9/os.py", line 225, in makedirs
   mkdir(name, mode)
   ```
   
   Solution:
   ```bash
   # The app.py file has been updated with a get_lambda_safe_path helper function
   # This ensures all paths are properly converted to use /tmp in Lambda
   # The helper function uses the pattern: filepath = '/tmp/' + key
   # To apply the fix, simply redeploy:
   ./deploy.sh YOUR_OPENAI_API_KEY
   ```

5. **S3 Bucket Issues**:
   - Verify that your S3 bucket exists and the Lambda function has permissions to access it
   - Check that the S3_BUCKET environment variable is correctly set in the Lambda function

### 404 Not Found Error

If you're getting a 404 Not Found error:

1. **Check API Gateway Configuration**:
   - Verify that your API Gateway is correctly configured with the Lambda integration
   - Ensure the route is correct in your API request

2. **Test the API Directly**:
   ```bash
   # Test with the correct endpoint
   curl -X POST https://your-api-id.execute-api.your-region.amazonaws.com/generate \
     -H "Content-Type: application/json" \
     -d '{
       "description": "AWS web app with EC2 and RDS",
       "provider": "aws"
     }'
   ```

## Deployment Checklist

Before deploying:

1. ✅ Ensure your OpenAI API key is valid
2. ✅ Verify that your ECR repository exists
3. ✅ Check that your S3 bucket is properly configured
4. ✅ Make sure you're using a valid OpenAI model name in the code

## Testing Your Deployment

After deploying:

1. ✅ Test the health endpoint:
   ```bash
   curl https://your-api-id.execute-api.your-region.amazonaws.com/health
   ```

2. ✅ Test the generate endpoint:
   ```bash
   curl -X POST https://your-api-id.execute-api.your-region.amazonaws.com/generate \
     -H "Content-Type: application/json" \
     -d '{
       "description": "AWS web app with EC2 and RDS",
       "provider": "aws"
     }'
   ```
