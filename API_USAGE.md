# API Usage Guide

## 1. Generate a Diagram

**Endpoint:** `POST /generate`

**Description:**
Generate a diagram from a natural language description using the diagrams library and OpenAI API.



**Request Body (JSON):**
```
{
  "description": "<Your architecture description>",
  "provider": "aws"   // Optional: "aws", "azure", or "gcp". If omitted or invalid, defaults to generic instructions.
}
```


**Note:**
- The `provider` field is optional. If set to `"aws"`, `"azure"`, or `"gcp"`, the API will use cloud-specific instructions for the LLM. If omitted or unrecognized, generic instructions are used.
- The OpenAI API key must be set as the `OPENAI_API_KEY` environment variable on the server or Docker container. **Do not** include the API key in the request body.


**Response (Success):**
```
{
  "diagram_files": {
    "png": "/diagrams/generated_diagram.png",
    "svg": "/diagrams/generated_diagram.svg",
    "pdf": "/diagrams/generated_diagram.pdf",
    "dot": "/diagrams/generated_diagram.dot",
    "jpg": "/diagrams/generated_diagram.jpg"
  }
}
```

All available formats will be included in the `diagram_files` object. The keys are the file formats, and the values are the URLs to access each format.

**Response (Error):**
```
{
  "error": "<error message>"
}
```



**Example cURL:**
```
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "description": "AWS web app with EC2 and RDS",
    "provider": "aws"
  }'
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
curl http://localhost:5000/diagrams/generated_diagram.png --output diagram.png
```

---

## Error Handling
- All errors return JSON with an `error` field and appropriate HTTP status code.
- Common errors: missing fields, invalid API key, unsupported imports, code execution errors.

---

## Troubleshooting
- Ensure your OpenAI API key is valid and has sufficient quota.
- Check `app.log` for server-side errors.
- Make sure Graphviz and all Python dependencies are installed.
- If diagrams are not generated, inspect the raw code in `diagrams/generated_diagram_raw.py`.
