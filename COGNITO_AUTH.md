# Using Cognito JWT Authentication with API Gateway

This guide explains how to use the Cognito JWT authentication that has been integrated with your API Gateway.

## Overview

The infrastructure has been updated to add JWT-based authentication using Amazon Cognito. This means that:

1. Your API endpoints are now protected by Cognito authentication
2. Clients need to authenticate with Cognito and include a valid JWT token in their requests
3. You can use the Cognito user management features (user registration, login, forgot password, etc.)

## Configuration Options

The Terraform configuration supports two modes:

1. **Create New Cognito Resources**: By default, it will create a new Cognito User Pool and Client
2. **Use Existing Cognito**: You can connect to an existing Cognito User Pool by setting `use_existing_cognito = true` and providing the existing User Pool ID and Client ID

## How to Get a JWT Token

### Using the Cognito Hosted UI

1. Access the Cognito hosted UI at: `https://<your-cognito-domain-prefix>.auth.<region>.amazoncognito.com/login?client_id=<client-id>&response_type=token&scope=email+openid+profile&redirect_uri=<callback-url>`

2. Sign up for a new account or sign in with an existing account

3. After successful authentication, Cognito will redirect to your callback URL with the tokens in the URL fragment

### Using the Cognito API

Alternatively, you can use the Cognito API directly:

```javascript
// Example using AWS Amplify
import { Auth } from 'aws-amplify';

Auth.configure({
  userPoolId: 'YOUR_USER_POOL_ID',
  userPoolWebClientId: 'YOUR_CLIENT_ID',
  region: 'YOUR_REGION'
});

// Sign up
async function signUp(username, password, email) {
  try {
    await Auth.signUp({
      username,
      password,
      attributes: { email }
    });
  } catch (error) {
    console.error('Error signing up:', error);
  }
}

// Sign in and get JWT token
async function signIn(username, password) {
  try {
    const user = await Auth.signIn(username, password);
    const session = user.signInUserSession;
    const idToken = session.idToken.jwtToken;
    const accessToken = session.accessToken.jwtToken;
    return { idToken, accessToken };
  } catch (error) {
    console.error('Error signing in:', error);
  }
}
```

## Making Authenticated API Requests

Once you have the JWT token, include it in the Authorization header of your API requests:

```javascript
// Example fetch request with JWT token
async function callProtectedApi(jwtToken) {
  try {
    const response = await fetch('https://your-api-endpoint/generate', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${jwtToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        description: 'AWS web app with EC2 and RDS',
        provider: 'aws'
      })
    });
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error calling API:', error);
  }
}
```

## Connecting to an Existing Cognito User Pool

If you already have a Cognito User Pool that you want to use:

1. Edit `terraform.tfvars` and set:
   ```
   use_existing_cognito = true
   existing_cognito_user_pool_id = "YOUR_USER_POOL_ID"
   existing_cognito_user_pool_client_id = "YOUR_CLIENT_ID"
   ```

2. Make sure your existing Cognito User Pool Client is configured correctly:
   - Has the appropriate callback URLs
   - Has OAuth flows enabled (implicit, code)
   - Has the necessary scopes (email, openid, profile)

3. Apply the Terraform changes:
   ```
   cd infrastructure
   terraform apply
   ```

## Testing the Authentication

You can test your protected API using curl:

```bash
# First get a token (you'll need to do this through the Cognito hosted UI or SDK)
TOKEN="your-jwt-token"

# Then call the protected API
curl -X POST https://your-api-endpoint/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "AWS web app with EC2 and RDS",
    "provider": "aws"
  }'
```

The public health endpoint should still be accessible without authentication:

```bash
curl https://your-api-endpoint/health
```

## Troubleshooting

1. **401 Unauthorized Error**: Check that your JWT token is valid and not expired

2. **Invalid Token Error**: Ensure you're using the correct token (ID token or Access token) as required by your authorizer

3. **CORS Issues**: If you're calling the API from a browser, make sure CORS is properly configured

4. **Token Format**: The token should be included as `Bearer <token>` in the Authorization header
