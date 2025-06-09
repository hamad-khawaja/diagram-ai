# Standard library imports
import os
import re
import hashlib
import json
from functools import lru_cache

# Third-party imports
from openai import OpenAI

# Simple in-memory cache for LLM responses
_cache = {}

def _get_cache_key(model, messages, temperature, max_tokens):
    """Generate a cache key based on the request parameters"""
    key_dict = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    key_str = json.dumps(key_dict, sort_keys=True)
    return hashlib.md5(key_str.encode()).hexdigest()

def openai_chat_with_cache(model, messages, temperature=0, max_tokens=15000, top_p=1, use_cache=True):
    """Make an OpenAI API call with caching"""
    # Generate a cache key
    cache_key = _get_cache_key(model, messages, temperature, max_tokens)
    
    # Check if we have a cached response
    if use_cache and cache_key in _cache:
        print(f"Cache hit for {model} request")
        return _cache[cache_key]
    
    # No cache hit, make the actual API call
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key or not api_key.startswith("sk-"):
        raise ValueError("OPENAI_API_KEY environment variable is missing or invalid.")
    
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p
    )
    
    # Cache the response
    if use_cache:
        _cache[cache_key] = response
    
    return response
def generate_explanation_openai(prompt):
    messages = [
        {"role": "system", "content": "You are a helpful cloud architecture assistant."},
        {"role": "user", "content": prompt}
    ]
    response = openai_chat_with_cache(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0,
        max_tokens=4000,  # Reduced to be within model limits (GPT-3.5-Turbo supports max 4096 tokens)
        top_p=0.7
    )
    return response.choices[0].message.content.strip()

def generate_code_openai(description, instructions):
    messages = [
        {"role": "system", "content": instructions},
        {"role": "user", "content": description}
    ]
    response = openai_chat_with_cache(
        model="gpt-4o",
        messages=messages,
        temperature=0,
        max_tokens=15024,
        top_p=1,
        use_cache=False  # Disable caching for code generation to ensure freshness
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
    messages = [
        {"role": "system", "content": instructions},
        {"role": "user", "content": user_input}
    ]
    response = openai_chat_with_cache(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0,
        max_tokens=4000,  # Reduced to be within model limits (GPT-3.5-Turbo supports max 4096 tokens)
        top_p=1
    )
    return response.choices[0].message.content.strip()
