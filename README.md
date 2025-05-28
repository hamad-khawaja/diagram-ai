# AI Diagram Generator API

This project provides a robust, secure, and user-friendly Python Flask API for generating diagrams from user descriptions using OpenAI GPT-4.1 and the diagrams library. It is fully containerized with Docker.

## Prerequisites
- [Docker](https://docs.docker.com/get-docker/) installed on your system
- An OpenAI API key (for GPT-4.1 access)

## Quick Start (Docker)

### 1. Clone the repository
```
git clone <your-repo-url>
cd mingrammer
```

### 2. Build the Docker image
```
docker build -t mingrammer-diagram-api .
```

### 3. Run the Docker container
Replace `YOUR_OPENAI_API_KEY` with your actual OpenAI API key:
```
docker run -d \
  -e OPENAI_API_KEY=YOUR_OPENAI_API_KEY \
  -p 5000:5000 \
  --name mingrammer-diagram-api \
  mingrammer-diagram-api
```

- The API will be available at: http://localhost:5000

### 4. Test the API
See `API_USAGE.md` for endpoint documentation and example requests.

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
5. Run the app:
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
