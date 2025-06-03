def fix_dot_inplace(dot_path):
    try:
        # Call the fix_dot_icons.py script to overwrite the DOT in place
        result = sp.run([
            sys.executable, os.path.join(os.path.dirname(__file__), 'fix_dot_icons.py'),
            dot_path, dot_path
        ], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"[DEBUG] Fixed DOT icons in {dot_path}")
        else:
            logger.warning(f"[DEBUG] fix_dot_icons.py failed for {dot_path}: {result.stderr}")
    except Exception as e:
        logger.warning(f"[DEBUG] Exception running fix_dot_icons.py for {dot_path}: {e}")
import sys
import subprocess as sp
def fix_svg_inplace(svg_path):
    try:
        # Call the fix_svg_icons.py script to overwrite the SVG in place
        result = sp.run([
            sys.executable, os.path.join(os.path.dirname(__file__), 'fix_svg_icons.py'),
            svg_path, svg_path
        ], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"[DEBUG] Fixed SVG icons in {svg_path}")
        else:
            logger.warning(f"[DEBUG] fix_svg_icons.py failed for {svg_path}: {result.stderr}")
    except Exception as e:
        logger.warning(f"[DEBUG] Exception running fix_svg_icons.py for {svg_path}: {e}")

# --- LLM Provider and Logging Setup ---
import os
import logging

LLM_PROVIDER = os.environ.get('LLM_PROVIDER', 'openai').strip().lower()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
print(f"[DEBUG] Using LLM provider: {LLM_PROVIDER}")
logger.info(f"[DEBUG] Using LLM provider: {LLM_PROVIDER}")

from flask import Flask, request, jsonify, send_from_directory, render_template_string
from werkzeug.utils import secure_filename
from flask_cors import CORS
import uuid
from llm_providers import (
    generate_code_openai, generate_explanation_openai,
    generate_code_gemini, generate_explanation_gemini
)

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "http://localhost:3000"])
UPLOAD_FOLDER = 'diagrams/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# New endpoint: Explain diagram code
@app.route('/explain', methods=['POST'])
def explain_diagram():
    data = request.json
    code = data.get('code')
    if not code or not isinstance(code, str):
        return error_response('Valid Python code is required for explanation.', 400)
    prompt = (
        "Given the following diagrams Python code, provide a short, detailed, bullet-point explanation "
        "of the flow and architecture. Be concise but clear. Do not exceed 8 bullet points.\n\n"
        "Code:\n"
        f"{code}"
    )
    try:
        explanation = generate_explanation_openai(prompt)
        return jsonify({'explanation': explanation})
    except Exception as e:
        return error_response(f'Failed to generate explanation: {str(e)}', 500)
import os
import json
import logging
from flask import Flask, request, jsonify, send_from_directory, render_template_string
from werkzeug.utils import secure_filename
from flask_cors import CORS
import uuid


app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "http://localhost:3000"])
UPLOAD_FOLDER = 'diagrams/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# --- Shared error response helper ---
def error_response(message, status=400, **kwargs):
    logger.error(f"API error: {message}")
    resp = {'error': message}
    resp.update(kwargs)
    return jsonify(resp), status

# Static file serving for diagrams folder with error handling and logging
@app.route('/diagrams/<path:filename>')
def serve_diagram_file(filename):
    try:
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.isfile(file_path):
            logger.warning(f"Requested diagram file not found: {file_path}")
            return error_response(f'Diagram file not found: {filename}', 404)
        logger.info(f"Serving diagram file: {file_path}")
        return send_from_directory(UPLOAD_FOLDER, filename)
    except Exception as e:
        logger.error(f"Error serving diagram file {filename}: {e}")
        return error_response(f'Failed to serve diagram file: {filename}', 500)



from llm_providers import generate_code_openai, generate_explanation_openai

@app.route('/generate', methods=['POST'])

def generate_diagram():
    # Predefine code URLs for error handling
    raw_code_url = '/diagrams/generated_diagram_raw.py'
    sanitized_code_url = '/diagrams/generated_diagram.py'
    import re, subprocess, traceback, resource
    from diagrams_whitelist import is_code_whitelisted

    data = request.json
    description = data.get('description') if data else None
    if not isinstance(description, str) or not description.strip():
        return error_response('Description must be a non-empty string.', 400)
    if len(description) > 15000:
        return error_response('Description is too long (max 15000 chars).', 400)


    provider = data.get('provider') if data else None
    provider = provider.strip().lower() if provider else None
    provider_map = {
        'aws': 'instructions_aws.md',
        'azure': 'instructions_azure.md',
        'gcp': 'instructions_gcp.md'
    }
    instructions_file = provider_map.get(provider)
    if not instructions_file:
        return error_response('No cloud provider specified. Please set provider to aws, azure, or gcp.', 400)


    try:
        with open(instructions_file, 'r') as f:
            instructions = f.read()
    except Exception as e:
        return error_response(f'Failed to read {instructions_file}: {e}', 500)


    # Generate code with selected LLM (from env)
    try:
        logger.info(f"[DEBUG] LLM_PROVIDER in generate_diagram: {LLM_PROVIDER}")
        logger.info(f"[DEBUG] Description: {description}")
        logger.info(f"[DEBUG] Instructions file: {instructions_file}")
        if LLM_PROVIDER == 'gemini':
            logger.info("[DEBUG] Calling generate_code_gemini...")
            code = generate_code_gemini(description, instructions)
            logger.info("Code generated by Gemini successfully.")
        else:
            logger.info("[DEBUG] Calling generate_code_openai...")
            code = generate_code_openai(description, instructions)
            logger.info("Code generated by OpenAI successfully.")
    except Exception as e:
        tb = traceback.format_exc()
        logger.error(f"[DEBUG] Exception in code generation: {e}\n{tb}")
        if LLM_PROVIDER == 'openai' and ((hasattr(e, 'status_code') and e.status_code == 429) or 'quota' in str(e).lower() or 'rate limit' in str(e).lower()):
            return error_response(
                'OpenAI API quota exceeded. Please check your plan and billing at https://platform.openai.com/account/usage',
                429,
                raw_code_url=None,
                sanitized_code_url=None
            )
        return error_response(f'{LLM_PROVIDER.capitalize()} API error: {str(e)}', 500, traceback=tb)

    # Check for non-code or fallback LLM responses
    if code.strip().lower().startswith("sorry") or not ("import" in code or "with Diagram" in code):
        user_msg = code.strip().splitlines()[0] if code.strip() else "The model could not generate valid code for your request."
        return error_response(f"The model could not generate valid code for your request: {user_msg}", 422)

    # Save raw code
    raw_code_path = os.path.join(UPLOAD_FOLDER, 'generated_diagram_raw.py')
    try:
        with open(raw_code_path, 'w') as f:
            f.write(code)
        logger.info(f"Raw code saved to {raw_code_path}")
    except Exception as e:
        return error_response('Failed to save raw code', 500)

    # Whitelist check
    allowed, bad_line = is_code_whitelisted(code)
    if not allowed:
        # Try to extract the invalid resource/class name for a more helpful error
        import re
        m = re.match(r'from diagrams\.([a-z]+)\.([a-z_]+) import (.+)', bad_line)
        if m:
            provider, category, resources = m.groups()
            # Check which resource is invalid (if multiple, comma-separated)
            invalids = []
            for res in [r.strip() for r in resources.split(",")]:
                try:
                    __import__(f'diagrams.{provider}.{category}', fromlist=[res])
                    if not hasattr(__import__(f'diagrams.{provider}.{category}', fromlist=[res]), res):
                        invalids.append(res)
                except Exception:
                    invalids.append(res)
            if invalids:
                return error_response(
                    f"The following resource(s) are not valid in diagrams.{provider}.{category}: {', '.join(invalids)}.",
                    400,
                    raw_code_file=raw_code_path
                )
        # Fallback generic error
        return error_response(f'Invalid or unsupported import in generated code: {bad_line}', 400, raw_code_file=raw_code_path)

    # Sanitize code
    code = re.sub(r'filename\s*=\s*["\']([^"\']+)["\']', 'filename="generated_diagram"', code)
    code = re.sub(r'outformat\s*=\s*["\']([^"\']+)["\']', 'outformat="png"', code)
    # Always inject show=False into every with Diagram(...) statement
    def _inject_show_false(match):
        args = match.group(1)
        if 'show=' in args:
            # Replace any show=... with show=False
            args = re.sub(r'show\s*=\s*\w+', 'show=False', args)
        else:
            if args.strip():
                args = args.strip() + ', show=False'
            else:
                args = 'show=False'
        return f'with Diagram({args})'
    code = re.sub(r'with Diagram\(([^)]*)\)', _inject_show_false, code)

    # Generate explanation (always, for now)
    explanation = None
    try:
        explanation_prompt = (
            "Given the following diagrams Python code, provide a short, detailed, bullet-point explanation "
            "of the flow and architecture. Be concise but clear. Do not exceed 8 bullet points.\n\n"
            "Code:\n"
            f"{code}"
        )
        logger.info(f"[DEBUG] Explanation prompt: {explanation_prompt[:200]}...")
        if LLM_PROVIDER == 'gemini':
            logger.info("[DEBUG] Calling generate_explanation_gemini...")
            explanation = generate_explanation_gemini(explanation_prompt)
        else:
            logger.info("[DEBUG] Calling generate_explanation_openai...")
            explanation = generate_explanation_openai(explanation_prompt)
    except Exception as e:
        logger.error(f"[DEBUG] Failed to generate explanation: {e}")
        explanation = None

    # Save explanation as Markdown file
    try:
        md_path = os.path.join(UPLOAD_FOLDER, 'generated_diagram.md')
        with open(md_path, 'w') as f:
            f.write(explanation or "(No explanation generated)")
        logger.info(f"Explanation saved to {md_path}")
    except Exception as e:
        logger.error(f"Failed to save explanation markdown: {e}")
    sanitized_code_path = os.path.join(UPLOAD_FOLDER, 'generated_diagram.py')
    try:
        with open(sanitized_code_path, 'w') as f:
            f.write(code)
        logger.info(f"Sanitized code saved to {sanitized_code_path}")
    except Exception as e:
        return error_response('Failed to save sanitized code', 500)

    # Run diagram code
    cwd = os.getcwd()
    try:
        os.chdir(UPLOAD_FOLDER)
        try:
            proc = subprocess.run(
                ['python3', 'generated_diagram.py'],
                capture_output=True,
                text=True,
                timeout=60
            )
            logger.info(f"Diagram code executed. Return code: {proc.returncode}")
            if proc.returncode != 0:
                logger.error(f"Diagram code execution failed. Stderr: {proc.stderr}\nStdout: {proc.stdout}")
                # If it's a SyntaxError or the code is not valid Python, return 422
                if 'SyntaxError' in proc.stderr or 'invalid syntax' in proc.stderr:
                    response_data = {
                        'error': 'Diagram code execution failed due to invalid or non-Python code.',
                        'stderr': proc.stderr,
                        'stdout': proc.stdout,
                        'raw_code_url': raw_code_url,
                        'sanitized_code_url': sanitized_code_url
                    }
                    logger.error("API response to frontend: %s", json.dumps(response_data, indent=2))
                    return jsonify(response_data), 422
                # If it's a TypeError for list >> list, return a user-friendly error
                if 'TypeError' in proc.stderr and 'unsupported operand type(s) for >>' in proc.stderr:
                    response_data = {
                        'error': 'Diagram code execution failed: You cannot use >> between lists of nodes. Connect nodes individually or use a nested loop.',
                        'stderr': proc.stderr,
                        'stdout': proc.stdout,
                        'raw_code_url': raw_code_url,
                        'sanitized_code_url': sanitized_code_url
                    }
                    logger.error("API response to frontend: %s", json.dumps(response_data, indent=2))
                    return jsonify(response_data), 422
                # Try to return the diagram if it was generated, even if there was an error
                image_candidates = []
                try:
                    with open('generated_diagram.py', 'r') as f:
                        code_content = f.read()
                    m = re.search(r'filename\s*=\s*["\']([^"\']+)["\']', code_content)
                    if m:
                        base = m.group(1)
                        base_png = base if base.endswith('.png') else base + '.png'
                        image_candidates.append(base_png)
                        image_candidates.append(os.path.basename(base_png))
                    else:
                        m2 = re.search(r'with Diagram\((?:["\'])(.*?)(?:["\'])', code_content)
                        if m2:
                            title = m2.group(1)
                            title_clean = title.lower().replace(' ', '_').replace('/', '_')
                            image_candidates.append(title_clean + '.png')
                except Exception as e:
                    logger.warning(f"Could not infer image filename from code: {e}")
                for candidate in image_candidates:
                    if os.path.exists(candidate):
                        image_url = f'/diagrams/{candidate.replace(os.sep, "/")}'
                        response_data = {
                            'diagram_path': candidate,
                            'image_url': image_url,
                            'error': 'Diagram code execution failed',
                            'stderr': proc.stderr,
                            'stdout': proc.stdout
                        }
                        logger.error("API response to frontend: %s", json.dumps(response_data, indent=2))
                        return jsonify(response_data), 206
                # Fallback: search for any .png in folder
                for fname in os.listdir('.'):
                    if fname.endswith('.png'):
                        image_url = f'/diagrams/{fname.replace(os.sep, "/")}'
                        response_data = {
                            'diagram_path': fname,
                            'image_url': image_url,
                            'error': 'Diagram code execution failed',
                            'stderr': proc.stderr,
                            'stdout': proc.stdout
                        }
                        logger.error("API response to frontend: %s", json.dumps(response_data, indent=2))
                        return jsonify(response_data), 206
                response_data = {
                    'error': 'Diagram code execution failed',
                    'stderr': proc.stderr,
                    'stdout': proc.stdout,
                    'raw_code_url': raw_code_url,
                    'sanitized_code_url': sanitized_code_url
                }
                logger.error("API response to frontend: %s", json.dumps(response_data, indent=2))
                return jsonify(response_data), 500
        except Exception as e:
            logger.error(f"Diagram execution error: {e}")
            return error_response(f'Diagram execution error: {str(e)}', 500)
    finally:
        os.chdir(cwd)

    # Collect output files
    output_formats = ["png", "svg", "pdf", "dot", "jpg"]
    base_names = set()
    try:
        with open(sanitized_code_path, 'r') as f:
            code_content = f.read()
        m = re.search(r'filename\s*=\s*["\']([^"\']+)["\']', code_content)
        if m:
            base = m.group(1)
            base_png = base if base.endswith('.png') else base + '.png'
            base_names.add(os.path.splitext(os.path.basename(base_png))[0])
        else:
            m2 = re.search(r'with Diagram\((?:["\'])(.*?)(?:["\'])', code_content)
            if m2:
                title = m2.group(1)
                title_clean = title.lower().replace(' ', '_').replace('/', '_')
                base_names.add(title_clean)
    except Exception as e:
        logger.warning(f"Could not infer image filename from code: {e}")
    # Fallback: search for any output file in UPLOAD_FOLDER and subfolders
    for root, dirs, files in os.walk(UPLOAD_FOLDER):
        for fname in files:
            for ext in output_formats:
                if fname.endswith('.' + ext):
                    base = os.path.splitext(fname)[0]
                    base_names.add(base)
                    # If SVG, fix icons in place by running the script
                    if ext == "svg":
                        svg_path = os.path.join(root, fname)
                        fix_svg_inplace(svg_path)

    if base_names:
        urls = {}
        for base in base_names:
            for ext in output_formats:
                fpath = os.path.join(UPLOAD_FOLDER, f"{base}.{ext}")
                if os.path.exists(fpath):
                    rel_path = os.path.relpath(fpath, UPLOAD_FOLDER)
                    urls[ext] = f'/diagrams/{rel_path.replace(os.sep, "/")}'
        logger.info(f"Diagram files generated: {urls}")
        raw_code_url = '/diagrams/generated_diagram_raw.py'
        sanitized_code_url = '/diagrams/generated_diagram.py'
        return jsonify({
            'diagram_files': urls,
            'raw_code_url': raw_code_url,         # Only URL for raw code, not the code itself
            'sanitized_code_url': sanitized_code_url,
            'explanation': explanation,
            'explanation_md_url': '/diagrams/generated_diagram.md'
        })

    # Final fallback: should never be reached, but ensures a response is always sent
    return error_response('Unknown server error', 500)


if __name__ == '__main__':
    app.run(port=5050)
