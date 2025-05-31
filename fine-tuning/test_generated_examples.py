import json
import os
import tempfile
import subprocess
import pytest

import itertools

def load_examples(*filenames):
    for fname in filenames:
        if os.path.exists(fname):
            with open(fname) as f:
                for line in f:
                    yield json.loads(line)

@pytest.mark.parametrize("example", list(load_examples("advanced_examples.jsonl", "custom_examples.jsonl")))
def test_diagram_code_runs(example):
    # Extract the code from the assistant's message

    # Extract code block from either 'completion' (advanced_examples) or 'messages' (custom_examples)
    import re
    code = ""
    if "completion" in example:
        completion = example.get("completion", "")
        # Find the first Python code block
        match = re.search(r"```python(.*?)```", completion, re.DOTALL)
        if match:
            code = match.group(1).strip()
        else:
            # Fallback: try to find any code block
            match = re.search(r"```(.*?)```", completion, re.DOTALL)
            if match:
                code = match.group(1).strip()
    elif "messages" in example:
        # Find the first assistant message with code content
        for msg in example["messages"]:
            if msg.get("role") == "assistant":
                # Try to extract code block from content
                content = msg.get("content", "")
                match = re.search(r"```python(.*?)```", content, re.DOTALL)
                if match:
                    code = match.group(1).strip()
                    break
                else:
                    match = re.search(r"```(.*?)```", content, re.DOTALL)
                    if match:
                        code = match.group(1).strip()
                        break
                # If no code block, fallback to using the whole content
                if not code and content.strip():
                    code = content.strip()
                    break
    assert code, "No code found in example completion or messages"

    # Run the code in a temp directory
    with tempfile.TemporaryDirectory() as tmpdir:
        code_file = os.path.join(tmpdir, "test_diagram.py")
        with open(code_file, "w") as f:
            f.write(code)
        try:
            result = subprocess.run(
                ["python3", code_file],
                cwd=tmpdir,
                capture_output=True,
                text=True,
                timeout=30
            )
            assert result.returncode == 0, f"Code failed: {result.stderr}\nStdout: {result.stdout}"
        except Exception as e:
            pytest.fail(f"Exception running code: {e}")
