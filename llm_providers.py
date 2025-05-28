
from openai import OpenAI

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
    match = re.search(r"```python(.*?)```", content, re.DOTALL | re.IGNORECASE)
    if match:
        code = match.group(1).strip()
    else:
        match = re.search(r"```(.*?)```", content, re.DOTALL)
        code = match.group(1).strip() if match else content.strip()
    return code
