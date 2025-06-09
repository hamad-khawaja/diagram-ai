# AI Diagram Generator API

This project delivers a robust, production-ready Flask API for automatically generating, validating, and explaining cloud architecture diagrams from natural language descriptions. Leveraging OpenAI’s GPT-4.1 and the Python diagrams library, the API transforms user prompts into executable Python code, produces multi-format architecture diagrams (PNG, SVG, PDF, etc.), and generates concise technical explanations in both plain text and Markdown. The system features advanced error handling, code sanitization, and supports provider-specific (AWS, Azure, GCP) instructions. All outputs and logs are accessible via secure endpoints, making this solution ideal for integrating AI-powered diagram generation into developer tools, documentation workflows, or educational platforms.

## Prerequisites
- [Docker](https://docs.docker.com/get-docker/) installed on your system
- An OpenAI API key (for GPT-4.1 access)

## Quick Start (Docker)


### 1. Clone the repository
Clone this repository to your local machine:
```
git clone https://github.com/hamadkhawaja/diagram-ai.git
cd diagram-ai
```

### 2. Build the Docker image

```
docker build -t diagram-ai-api .
```

### 3. Run the Docker container
Replace `YOUR_OPENAI_API_KEY` with your actual OpenAI API key:
```
docker run -d \
  -e OPENAI_API_KEY=YOUR_OPENAI_API_KEY \
  -e S3_BUCKET=<UPLOAD_BUCKET_NAME> \
  -p 5000:5000 \
  --name diagram-ai-api \
  diagram-ai-api
```

- The API will be available at: http://localhost:5000


### 4. Test the API
See `API_USAGE.md` for endpoint documentation and example requests.

**Multi-format Output:**
The API now returns URLs for all available diagram formats (PNG, SVG, PDF, DOT, JPG) in the response. You can access any format using the provided URLs.

---

## Development (Local, without Docker)
1. Install Python 3.10+ and [pip](https://pip.pypa.io/en/stable/installation/).
2. (Recommended) Create and activate a virtual environment:
   ```
   python -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Set your OpenAI API key as an environment variable:
   ```
   export OPENAI_API_KEY=YOUR_OPENAI_API_KEY
   ```
5. Set your S3 bucket name as an environment variable:
   ```
   export S3_BUCKET=<UPLOAD_BUCKET_NAME>
   ```

6. Run the app:
   ```
   python app.py
   ```

---

## Features
- **Diagram Generation**: Generate architecture diagrams from textual descriptions using OpenAI GPT-4.1 and the diagrams library.
- **Code Sanitization and Whitelisting**: Ensures generated code is safe and adheres to predefined rules.
- **Error Handling**: Logs errors and returns detailed JSON responses for debugging.
- **Static File Serving**: Serves generated diagrams via the `/diagrams/<filename>` endpoint.
- **Cloud Provider-Specific Instructions**: Supports AWS, Azure, and GCP-specific diagram generation using predefined instruction files.

## Key Features

1. **Natural Language to Diagram Generation**: Convert plain English descriptions into professional cloud architecture diagrams.

2. **Multi-Cloud Support**: Generate diagrams for AWS, Azure, and GCP using provider-specific terminology and best practices.

3. **Automatic Rewriting**: Input descriptions are automatically rewritten to use cloud provider-specific terminology and best practices before diagram generation.

4. **Multi-format Output**: All diagrams are available in PNG, SVG, PDF, DOT, and JPG formats.

5. **Intelligent Explanations**: Each diagram comes with an auto-generated technical explanation in plain text and Markdown.

## API Endpoints
### `/generate`
- **Method**: POST
- **Description**: Generates a diagram based on the provided description and cloud provider.
- **Request Body**:
  ```json
  {
    "description": "Your diagram description",
    "provider": "aws|azure|gcp"
  }
  ```
- **Response**:
  - Success: Returns the path and URL of the generated diagram.
  - Error: Returns an error message with details.

### `/diagrams/<filename>`
- **Method**: GET
- **Description**: Serves the generated diagram file.

## Logging
- Logs are saved to `app.log` for debugging and monitoring purposes.

## Additional Notes
- Ensure the `diagrams/` folder is writable for saving generated diagrams.
- The application uses `instructions_aws.md`, `instructions_azure.md`, and `instructions_gcp.md` for cloud-specific diagram generation.

## Troubleshooting
- If you encounter issues with Docker builds, try rebuilding with `--no-cache`:
  ```
  docker build --no-cache -t mingrammer-diagram-api .
  ```
- For API usage and troubleshooting, see `API_USAGE.md`.

## License
MIT

## Environment Variables

- `OPENAI_API_KEY` – Your OpenAI API key (required)
- `S3_BUCKET` – The name of your S3 bucket for storing generated files (required)

For Docker, add the S3_BUCKET variable to your `docker run` command:
```
docker run -d \
  -e OPENAI_API_KEY=YOUR_OPENAI_API_KEY \
  -e S3_BUCKET=<UPLOAD_BUCKET_NAME> \
  -p 5000:5000 \
  --name diagram-ai-api \
  diagram-ai-api
```
