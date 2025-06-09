# Standard library imports
import os
import re

# Third-party imports
from openai import OpenAI
def generate_explanation_openai(prompt):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key or not api_key.startswith("sk-"):
        raise ValueError("OPENAI_API_KEY environment variable is missing or invalid.")
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o",  # Use the more widely available gpt-4o model instead of gpt-4.1
        messages=[
            {"role": "system", "content": "You are a helpful cloud architecture assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0,
        max_tokens=15120,
        top_p=0.7
    )
    return response.choices[0].message.content.strip()

def generate_code_openai(description, instructions):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key or not api_key.startswith("sk-"):
        raise ValueError("OPENAI_API_KEY environment variable is missing or invalid.")
    client = OpenAI(api_key=api_key)
    prompt = f"""{instructions}\n\nUser request: {description}"""
    response = client.chat.completions.create(
        model="gpt-4o",  # Use the more widely available gpt-4o model instead of gpt-4.1
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

def generate_rewrite_openai(user_input, instructions):
    """
    Generate rewritten content using OpenAI's API based on rewrite instructions.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key or not api_key.startswith("sk-"):
        raise ValueError("OPENAI_API_KEY environment variable is missing or invalid.")
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": instructions},
            {"role": "user", "content": user_input}
        ],
        temperature=0,
        max_tokens=15024,
        top_p=1
    )
    return response.choices[0].message.content.strip()
