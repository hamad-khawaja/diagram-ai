import threading
# Gemini model selection (auto-detect best available)
def get_best_gemini_model():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[DEBUG] GEMINI_API_KEY missing for model selection!")
        return "gemini-2.0-flash"
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    try:
        resp = requests.get(endpoint)
        print(f"[DEBUG] Gemini ListModels status: {resp.status_code}")
        if not resp.ok:
            print(f"[DEBUG] Gemini ListModels error: {resp.text}")
            return "gemini-2.0-flash"
        data = resp.json()
        models = [m["name"] for m in data.get("models", [])]
        # Prefer pro models, then highest version
        pro_models = [m for m in models if "pro" in m]
        if pro_models:
            best = sorted(pro_models, reverse=True)[0]
            print(f"[DEBUG] Best Gemini pro model: {best}")
            return best
        if models:
            best = sorted(models, reverse=True)[0]
            print(f"[DEBUG] Best Gemini model: {best}")
            return best
    except Exception as e:
        print(f"[DEBUG] Exception in Gemini model selection: {e}")
    return "gemini-2.0-flash"

# Run model selection at import time (in a thread to avoid blocking startup)
GEMINI_MODEL = "gemini-2.0-flash"
def _set_best_gemini_model():
    global GEMINI_MODEL
    try:
        GEMINI_MODEL = get_best_gemini_model()
        print(f"[DEBUG] Using Gemini model: {GEMINI_MODEL}")
    except Exception as e:
        print(f"[DEBUG] Exception in Gemini model selection thread: {e}")
        GEMINI_MODEL = "gemini-2.0-flash"
        print(f"[DEBUG] Falling back to default Gemini model: {GEMINI_MODEL}")
threading.Thread(target=_set_best_gemini_model, daemon=True).start()
def generate_explanation_openai(prompt):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key or not api_key.startswith("sk-"):
        raise ValueError("OPENAI_API_KEY environment variable is missing or invalid.")
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "You are a helpful cloud architecture assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0,
        max_tokens=15120,
        top_p=0.7
    )
    return response.choices[0].message.content.strip()


import requests
from openai import OpenAI
def generate_code_gemini(description, instructions):
    print("[DEBUG] Entered generate_code_gemini")
    api_key = os.environ.get("GEMINI_API_KEY")
    print(f"[DEBUG] GEMINI_API_KEY present: {bool(api_key)}")
    if not api_key:
        print("[DEBUG] GEMINI_API_KEY missing or invalid!")
        raise ValueError("GEMINI_API_KEY environment variable is missing or invalid.")
    model = GEMINI_MODEL
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key=" + api_key
    prompt = f"{instructions}\n\nUser request: {description}"
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }
    print(f"[DEBUG] Gemini endpoint: {endpoint}")
    print(f"[DEBUG] Gemini payload: {payload}")
    response = requests.post(endpoint, json=payload)
    print(f"[DEBUG] Gemini response status: {response.status_code}")
    print(f"[DEBUG] Gemini response text: {response.text[:500]}")
    if not response.ok:
        raise Exception(f"Gemini API error: {response.text}")
    data = response.json()
    content = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
    return extract_python_code(content)

def generate_explanation_gemini(prompt):
    print("[DEBUG] Entered generate_explanation_gemini")
    api_key = os.environ.get("GEMINI_API_KEY")
    print(f"[DEBUG] GEMINI_API_KEY present: {bool(api_key)}")
    if not api_key:
        print("[DEBUG] GEMINI_API_KEY missing or invalid!")
        raise ValueError("GEMINI_API_KEY environment variable is missing or invalid.")
    model = GEMINI_MODEL
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key=" + api_key
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }
    print(f"[DEBUG] Gemini endpoint: {endpoint}")
    print(f"[DEBUG] Gemini payload: {payload}")
    response = requests.post(endpoint, json=payload)
    print(f"[DEBUG] Gemini response status: {response.status_code}")
    print(f"[DEBUG] Gemini response text: {response.text[:500]}")
    if not response.ok:
        raise Exception(f"Gemini API error: {response.text}")
    data = response.json()
    content = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
    return content.strip()

import os
from openai import OpenAI

def generate_code_openai(description, instructions):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key or not api_key.startswith("sk-"):
        raise ValueError("OPENAI_API_KEY environment variable is missing or invalid.")
    client = OpenAI(api_key=api_key)
    prompt = f"""{instructions}\n\nUser request: {description}"""
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": instructions},
            {"role": "user", "content": description}
        ],
        temperature=0,
        max_tokens=15024,
        top_p=1
    )
    content = response.choices[0].message.content
    return extract_python_code(content)

def extract_python_code(content):
    import re
    # Try to extract code from triple backticks (with or without python)
    match = re.search(r"```python(.*?)```", content, re.DOTALL | re.IGNORECASE)
    if match:
        code = match.group(1).strip()
    else:
        match = re.search(r"```(.*?)```", content, re.DOTALL)
        code = match.group(1).strip() if match else content.strip()

    # Remove any leading non-code lines (e.g., tool_code, explanations, etc.)
    code_lines = code.splitlines()
    # Find the first line that looks like valid Python (import, from, def, class, or with Diagram)
    for i, line in enumerate(code_lines):
        if re.match(r'^(import |from |def |class |with Diagram)', line.strip()):
            code = '\n'.join(code_lines[i:])
            break
    else:
        # If no valid code line found, return empty string
        code = ''

    # --- Post-process: Remove any Diagram.add_label calls (not supported by diagrams lib) ---
    code = re.sub(r"Diagram\\.add_label\\s*\\(.*?\\)\\s*", "", code)
    # Optionally, remove empty lines left by this
    code = '\n'.join([l for l in code.splitlines() if l.strip()])
    return code
