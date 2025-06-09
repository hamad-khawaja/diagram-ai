# API Usage Guide

## 1. Generate a Diagram

**Endpoint:** `POST /generate`

**Description:**
Generate a diagram from a natural language description using the diagrams library and OpenAI API.




**Request Body (JSON):**
```
{
  "description": "<Your architecture description>",
  "provider": "aws"        // Optional: "aws", "azure", or "gcp". If omitted or invalid, defaults to generic instructions.
}
```




**Note:**
- The `provider` field is optional. If set to `"aws"`, `"azure"`, or `"gcp"`, the API will use cloud-specific instructions for the LLM. If omitted or unrecognized, generic instructions are used.
- When a provider is specified, the description is automatically rewritten using cloud provider-specific terminology and best practices before diagram generation.
- The LLM provider is selected at app startup using the `LLM_PROVIDER` environment variable (`openai` or `gemini`).
- Set the appropriate API key as an environment variable: `OPENAI_API_KEY` for OpenAI, or `GEMINI_API_KEY` for Gemini. **Do not** include API keys in the request body.




**Response (Success):**
```
{
  "diagram_files": {
    "png": "/diagrams/generated_diagram.png",
    "svg": "/diagrams/generated_diagram.svg",
    "pdf": "/diagrams/generated_diagram.pdf",
    "dot": "/diagrams/generated_diagram.dot",
    "jpg": "/diagrams/generated_diagram.jpg"
  },
  "python_code": "<generated Python code as a string>",
  "raw_code_url": "/diagrams/generated_diagram_raw.py",
  "sanitized_code_url": "/diagrams/generated_diagram.py",
  "explanation": "<short, bullet-point explanation as a string>",
  "explanation_md_url": "/diagrams/generated_diagram.md"
}
```

- `diagram_files`: All available formats will be included as keys (e.g., `png`, `svg`, etc.) with URLs to access each format.
- `python_code`: The generated Python code as a string (for downstream use or inspection).
- `raw_code_url`: URL to download the raw generated code (before sanitization/whitelisting).
- `sanitized_code_url`: URL to download the sanitized code (safe for execution).
- `explanation`: A short, bullet-point summary of the generated architecture, produced by the LLM.
- `explanation_md_url`: URL to download the explanation as a Markdown file.


**Response (Error):**
```
{
  "error": "<error message>",
  "python_code": null,                // present for some errors
  "raw_code_url": null,               // present for some errors
  "sanitized_code_url": null          // present for some errors
}
```

**Special Error (OpenAI API Rate Limit):**
```
{
  "error": "OpenAI API quota exceeded. Please check your plan and billing at https://platform.openai.com/account/usage",
  "python_code": null,
  "raw_code_url": null,
  "sanitized_code_url": null
}
```
HTTP status code: 429






**Example cURL:**
```
curl -X POST http://localhost:5050/generate \
  -H "Content-Type: application/json" \
  -d '{
    "description": "AWS web app with EC2 and RDS",
    "provider": "aws"
  }'
```

**Example Success Response:**
```
{
  "diagram_files": {
    "png": "/diagrams/generated_diagram.png",
    "svg": "/diagrams/generated_diagram.svg"
  },
  "python_code": "from diagrams import Diagram...",
  "raw_code_url": "/diagrams/generated_diagram_raw.py",
  "sanitized_code_url": "/diagrams/generated_diagram.py",
  "explanation": "- Uses AWS Lambda for compute...\n- S3 is used for storage...",
  "explanation_md_url": "/diagrams/generated_diagram.md"
}
```

---

## LLM Prompt Best Practices

For best results when describing your architecture, see [`LLM_INPUT_TEMPLATE.md`](./LLM_INPUT_TEMPLATE.md) for a recommended prompt format and tips.

---

## 2. Retrieve a Generated Diagram

**Endpoint:** `GET /diagrams/<filename>`

**Description:**
Download or view a generated diagram image by filename.


**Example:**
```
curl http://localhost:5050/diagrams/generated_diagram.png --output diagram.png
```

---

## 2. Rewrite Content

**Endpoint:** `POST /rewrite`

**Description:**
Rewrite user input with cloud-specific terminology and best practices based on the specified provider.

**Request Body (JSON):**
```json
{
  "user_input": "<Your architecture description>",
  "provider": "aws"        // Required: "aws", "azure", or "gcp".
}
```

**Note:**
- The `provider` field is required and must be set to one of: `"aws"`, `"azure"`, or `"gcp"`. Each provider has specific rewrite instructions.
- The LLM provider is selected at app startup using the `LLM_PROVIDER` environment variable (`openai` or `gemini`).
- Set the appropriate API key as an environment variable: `OPENAI_API_KEY` for OpenAI, or `GEMINI_API_KEY` for Gemini.

**Response (Success):**
```json
{
  "rewritten_content": "<Rewritten content with cloud provider-specific terminology>",
  "provider": "aws"
}
```

**Response (Error):**
```json
{
  "error": "<Error message>",
  "status_code": 400
}
```

## 3. Explain Diagram Code

---

## Error Handling
- All errors return JSON with an `error` field and appropriate HTTP status code.
- For OpenAI API rate limits, a 429 status and a clear message are returned.
- Common errors: missing fields, invalid API key, unsupported imports, code execution errors, quota/rate limit exceeded.

---

## Troubleshooting
- Ensure your OpenAI or Gemini API key is valid and has sufficient quota.
- Set the `LLM_PROVIDER` environment variable to `openai` or `gemini` before starting the app.
- Check `app.log` for server-side errors.
- Make sure Graphviz and all Python dependencies are installed.
- If diagrams are not generated, inspect the raw code in `diagrams/generated_diagram_raw.py` (or download via `raw_code_url`).
