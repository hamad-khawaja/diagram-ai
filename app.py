# ===================
# Imports (Standard Library)
# ===================
import os
import sys
import re
import json
import uuid
import subprocess as sp
import traceback
import time
import concurrent.futures

# ===================
# Imports (Third-Party)
# ===================
from flask import Flask, request, jsonify, send_from_directory, render_template_string
from werkzeug.utils import secure_filename
from flask_cors import CORS
import boto3
from botocore.exceptions import ClientError
import boto3.s3.transfer

# ===================
# Imports (Local)
# ===================
from llm_providers import (
    generate_code_openai, generate_explanation_openai,
    generate_rewrite_openai
)
from parallel import generate_explanation_async

# ===================
# Global Variables & Constants
# ===================
S3_BUCKET = os.environ.get('S3_BUCKET')
if not S3_BUCKET:
    raise RuntimeError("S3_BUCKET environment variable is not set")
s3_client = boto3.client("s3")

# Define global UPLOAD_FOLDER - use /tmp for Lambda
# Check if running in Lambda environment
IS_LAMBDA = os.environ.get('AWS_LAMBDA_FUNCTION_NAME') is not None
if IS_LAMBDA:
    UPLOAD_FOLDER = '/tmp/diagrams/'
    # No need to create this directory at startup in Lambda
else:
    UPLOAD_FOLDER = 'diagrams/'
    # Only create the directory in non-Lambda environments
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Define a function to get Lambda-safe paths
def get_lambda_safe_path(path):
    """Convert a path to be Lambda-safe by ensuring it's in /tmp when in Lambda environment"""
    if IS_LAMBDA:
        # Strip any leading slashes from the path
        clean_path = path.lstrip('/')
        return '/tmp/' + clean_path
    else:
        return path



# ===================
# Flask App Setup
# ===================
app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "http://localhost:3000"])

# ===================
# Utility Functions
# ===================
def fix_svg_inplace(svg_path):
    try:
        # Instead of spawning a Python process, directly perform the necessary fix
        # This avoids process creation overhead
        with open(svg_path, 'r') as f:
            content = f.read()
            
        # Apply icon fixes (simplified version of what fix_svg_icons.py would do)
        # This is a basic implementation - adjust based on what fix_svg_icons.py actually does
        fixed_content = content
        
        # Common SVG fixes (example)
        if "<svg " in content and "xmlns=" not in content:
            fixed_content = content.replace("<svg ", '<svg xmlns="http://www.w3.org/2000/svg" ')
            
        # Write back only if changes were made
        if fixed_content != content:
            with open(svg_path, 'w') as f:
                f.write(fixed_content)
    except Exception as e:
        print(f"Error fixing SVG file: {str(e)}")

# New endpoint: Explain diagram code
@app.route('/explain', methods=['POST'])
def explain_diagram():
    data = request.json
    code = data.get('code')
    if not code or not isinstance(code, str):
        return error_response('Valid Python code is required for explanation.', 400)
    
    # Get provider from request if provided
    provider = data.get('provider') if data else None
    provider = provider.strip().lower() if provider else None
    
    # Original prompt to be used if no provider or rewriting fails
    original_prompt = (
        "Given the following diagrams Python code, provide a short, detailed, bullet-point explanation "
        "of the flow and architecture. Be concise but clear. Do not exceed 8 bullet points.\n\n"
        "Code:\n"
        f"{code}"
    )
    
    prompt = original_prompt
    
    # If provider is specified, rewrite the explanation prompt
    if provider and provider in ['aws', 'azure', 'gcp']:
        try:
            # Map providers to rewrite instruction files
            rewrite_provider_map = {
                'aws': 'instructions/rewrite/instructions_aws_rewrite.md',
                'azure': 'instructions/rewrite/instructions_azure_rewrite.md',
                'gcp': 'instructions/rewrite/instructions_gcp_rewrite.md'
            }
            
            rewrite_instructions_file = rewrite_provider_map.get(provider)
            
            # Verify the rewrite instructions file exists
            if rewrite_instructions_file and os.path.exists(rewrite_instructions_file):
                # Read the rewrite instructions
                with open(rewrite_instructions_file, 'r') as f:
                    rewrite_instructions = f.read()
                
                # Craft a provider-specific explanation prompt
                rewrite_prompt = (
                    f"I need to explain this {provider.upper()} architecture diagram code in the correct terminology. "
                    f"Please provide a bullet-point explanation using proper {provider.upper()} terminology for this code:\n\n{code}"
                )
                
                # Rewrite the prompt using OpenAI
                rewritten_prompt = generate_rewrite_openai(rewrite_prompt, rewrite_instructions)
                
                # Use the rewritten prompt if successful
                if rewritten_prompt:
                    prompt = rewritten_prompt
        except Exception as e:
            # If rewriting fails, continue with the original prompt
            print(f"Warning: Explanation prompt rewriting failed: {str(e)}. Continuing with original prompt.")
    
    try:
        explanation = generate_explanation_openai(prompt)
        response = {
            'explanation': explanation
        }
        
        # Include original and rewritten prompts if a rewrite was performed
        if prompt != original_prompt:
            response['original_prompt'] = original_prompt
            response['rewritten_prompt'] = prompt
            response['provider'] = provider
            
        return jsonify(response)
    except Exception as e:
        return error_response(f'Failed to generate explanation: {str(e)}', 500)


@app.route('/health', methods=['GET'])
def health():
    print(f"/health route hit. request.path: {request.path}, request.url: {request.url}")
    return jsonify({"status": "OK", "path": request.path, "url": request.url}), 200

# Improved catch-all route for all paths, including root
@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
def catch_all(path):
    print(f"catch_all route hit. path: {path}, request.path: {request.path}, method: {request.method}")
    print(f"request.headers: {dict(request.headers)}")
    print(f"request.data: {request.data}")
    
    # Special handling for root path
    if path == '' and request.method == 'GET':
        return index()
    
    return jsonify({
        "error": "Not Found",
        "path": path,
        "method": request.method,
        "request_path": request.path,
        "request_url": request.url,
        "headers": dict(request.headers)
    }), 404

@app.route('/')
def index():
    # Check if this is an API Gateway proxy integration
    if request.headers.get('x-forwarded-proto') or request.headers.get('x-api-gateway-event'):
        print("Detected API Gateway proxy integration")
        # Log all headers for debugging
        for header, value in request.headers.items():
            print(f"Header: {header}: {value}")
    
    return 'Diagram AI API is running. Please use the /generate endpoint with POST requests.', 200

# --- Shared error response helper ---
def error_response(message, status=400, **kwargs):
    # Logging removed
    resp = {'error': message}
    resp.update(kwargs)
    return jsonify(resp), status

# Static file serving for diagrams folder with error handling and logging
@app.route('/diagrams/<path:filename>')
def serve_diagram_file(filename):
    try:
        # Use our helper function to determine the base diagrams folder
        file_path = get_lambda_safe_path(os.path.join('diagrams', filename))
        
        # Check if file exists in the specified path
        if not os.path.isfile(file_path):
            # File not found
            return error_response(f'Diagram file not found: {filename}', 404)
        
        # Lambda can't serve files from /tmp directly through send_from_directory
        # In Lambda, serve files by reading and returning content
        if IS_LAMBDA:
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()
                
                # Set content type based on file extension
                content_type = 'image/png'  # Default
                if filename.endswith('.svg'):
                    content_type = 'image/svg+xml'
                elif filename.endswith('.pdf'):
                    content_type = 'application/pdf'
                elif filename.endswith('.dot'):
                    content_type = 'text/plain'
                elif filename.endswith('.py'):
                    content_type = 'text/plain'
                elif filename.endswith('.md'):
                    content_type = 'text/markdown'
                
                return content, 200, {'Content-Type': content_type}
            except Exception as e:
                return error_response(f'Failed to read diagram file: {str(e)}', 500)
        else:
            # For local development, use send_from_directory
            base_dir = 'diagrams'  # In non-Lambda, it's just the regular diagrams directory
            return send_from_directory(base_dir, filename)
    except Exception as e:
        # Logging removed
        return error_response(f'Failed to serve diagram file: {filename}', 500)



from llm_providers import generate_code_openai, generate_explanation_openai

@app.route('/generate', methods=['POST'])

def generate_diagram():
    print("request.data:", request.data)
    print("request.json:", request.json)
    timings = {}
    start_total = time.time()

    # LLM code generation
    start = time.time()
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
    if not provider:
        return error_response('No cloud provider specified. Please set provider to aws, azure, or gcp.', 400)

    # First, run the description through the rewrite endpoint
    original_description = description
    rewritten_description = None
    try:
        # Map providers to rewrite instruction files
        rewrite_provider_map = {
            'aws': 'instructions/rewrite/instructions_aws_rewrite.md',
            'azure': 'instructions/rewrite/instructions_azure_rewrite.md',
            'gcp': 'instructions/rewrite/instructions_gcp_rewrite.md'
        }
        
        rewrite_instructions_file = rewrite_provider_map.get(provider)
        
        # Verify the rewrite instructions file exists
        if rewrite_instructions_file and os.path.exists(rewrite_instructions_file):
            # Read the rewrite instructions
            with open(rewrite_instructions_file, 'r') as f:
                rewrite_instructions = f.read()
                
            # Rewrite the description using OpenAI
            rewritten_description = generate_rewrite_openai(description, rewrite_instructions)
                
            # Use the rewritten description instead of the original
            description = rewritten_description
    except Exception as e:
        # If rewriting fails, continue with the original description
        print(f"Warning: Description rewriting failed: {str(e)}. Continuing with original description.")
        rewritten_description = None

    # Map providers to instruction files in the /instructions/generate directory
    provider_map = {
        'aws': 'instructions/generate/instructions_aws_simplified.md',
        'azure': 'instructions/generate/instructions_azure_simplified.md',
        'gcp': 'instructions/generate/instructions_gcp_simplified.md'
    }
    provider_prefix = provider if provider in provider_map else 'unknown'
    instructions_file = provider_map.get(provider)
    if not instructions_file:
        return error_response('Invalid provider. Please use aws, azure, or gcp.', 400)

    # Verify the instructions file exists
    if not os.path.exists(instructions_file):
        return error_response(f'Instructions file not found at {instructions_file}. Please check your installation.', 500)


    try:
        with open(instructions_file, 'r') as f:
            instructions = f.read()
    except Exception as e:
        return error_response(f'Failed to read {instructions_file}: {e}', 500)


    # Generate code with OpenAI
    start_llm = time.time()
    try:
        # Generate code using OpenAI
        code = generate_code_openai(description, instructions)
    except Exception as e:
        tb = traceback.format_exc()
        if ((hasattr(e, 'status_code') and e.status_code == 429) or 'quota' in str(e).lower() or 'rate limit' in str(e).lower()):
            return error_response(
                'OpenAI API quota exceeded. Please check your plan and billing at https://platform.openai.com/account/usage',
                429,
                raw_code_url=None,
                sanitized_code_url=None
            )
        return error_response(f'OpenAI API error: {str(e)}', 500, traceback=tb)
    timings['llm'] = time.time() - start_llm

    # Check for non-code or fallback LLM responses
    if code.strip().lower().startswith("sorry") or not ("import" in code or "with Diagram" in code):
        user_msg = code.strip().splitlines()[0] if code.strip() else "The model could not generate valid code for your request."
        return error_response(f"The model could not generate valid code for your request: {user_msg}", 422)

    # --- Per-request temp directory, prefixed by provider ---
    import tempfile, shutil
    temp_uuid = str(uuid.uuid4())
    temp_dir_name = f"{provider_prefix}-{temp_uuid}"
    
    # Create a Lambda-safe path using our helper function
    temp_upload_folder = get_lambda_safe_path(os.path.join('diagrams', temp_dir_name))
    os.makedirs(temp_upload_folder, exist_ok=True)

    # Save raw code
    start_save_raw = time.time()
    raw_code_path = os.path.join(temp_upload_folder, 'generated_diagram_raw.py')
    try:
        with open(raw_code_path, 'w') as f:
            f.write(code)
        # Logging removed
    except Exception as e:
        # No need to clean up as Lambda automatically cleans up /tmp
        return error_response('Failed to save raw code', 500)
    timings['save_raw_code'] = time.time() - start_save_raw

    # Save original and rewritten descriptions
    start_save_inputs = time.time()
    try:
        # Save the original user input
        original_input_path = os.path.join(temp_upload_folder, 'original_input.txt')
        with open(original_input_path, 'w') as f:
            f.write(original_description or "")
            
        # Always save the rewritten description (use original if rewriting failed)
        rewritten_input_path = os.path.join(temp_upload_folder, 'rewritten_input.txt')
        with open(rewritten_input_path, 'w') as f:
            f.write(rewritten_description or original_description or "")
    except Exception as e:
        print(f"Warning: Failed to save input descriptions: {str(e)}")
        # Continue execution even if saving descriptions fails
    timings['save_inputs'] = time.time() - start_save_inputs

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

    # Save sanitized code before running it!
    start_save_sanitized = time.time()
    sanitized_code_path = os.path.join(temp_upload_folder, 'generated_diagram.py')
    try:
        with open(sanitized_code_path, 'w') as f:
            f.write(code)
        # Logging removed
    except Exception as e:
        # No need to clean up as Lambda automatically cleans up /tmp
        return error_response('Failed to save sanitized code', 500)
    timings['save_sanitized_code'] = time.time() - start_save_sanitized

    # --- Start explanation generation in parallel with diagram execution ---
    start_explanation = time.time()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit the explanation generation task to run in parallel
        explanation_future = executor.submit(generate_explanation_async, code, provider)
        
        # Run diagram code (in the main thread)
        start_exec = time.time()
        cwd = os.getcwd()
        try:
            os.chdir(temp_upload_folder)
            proc = subprocess.run(
                ['python3', 'generated_diagram.py'],
                capture_output=True,
                text=True,
                timeout=60
            )
            if proc.returncode != 0:
                # If it's a SyntaxError or the code is not valid Python, return 422
                if 'SyntaxError' in proc.stderr or 'invalid syntax' in proc.stderr:
                    response_data = {
                        'error': 'Diagram code execution failed due to invalid or non-Python code.',
                        'stderr': proc.stderr,
                        'stdout': proc.stdout,
                        'raw_code_url': raw_code_url,
                        'sanitized_code_url': sanitized_code_url
                    }
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
                    print(f"Could not infer image filename from code: {e}")
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
                        return jsonify(response_data), 206
                response_data = {
                    'error': 'Diagram code execution failed',
                    'stderr': proc.stderr,
                    'stdout': proc.stdout,
                    'raw_code_url': raw_code_url,
                    'sanitized_code_url': sanitized_code_url
                }
                return jsonify(response_data), 500
        except Exception as e:
            return error_response(f'Diagram execution error: {str(e)}', 500)
        finally:
            os.chdir(cwd)
            
        timings['diagram_execution'] = time.time() - start_exec
        
        # Now get the explanation result
        try:
            explanation = explanation_future.result()
        except Exception as e:
            print(f"Error getting explanation result: {str(e)}")
            explanation = None
            
    timings['explanation'] = time.time() - start_explanation

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
        print(f"Could not infer image filename from code: {e}")
    # Fallback: search for any output file in temp_upload_folder and subfolders
    for root, dirs, files in os.walk(temp_upload_folder):
        for fname in files:
            for ext in output_formats:
                if fname.endswith('.' + ext):
                    base = os.path.splitext(fname)[0]
                    base_names.add(base)
                    # If SVG, fix icons in place by running the script
                    if ext == "svg":
                        svg_path = os.path.join(root, fname)
                        fix_svg_inplace(svg_path)

    # Save explanation as Markdown file
    try:
        md_path = os.path.join(temp_upload_folder, 'generated_diagram.md')
        with open(md_path, 'w') as f:
            f.write(explanation or "(No explanation generated)")
    except Exception as e:
        print(f"Failed to save explanation markdown: {e}")

    # --- S3 Upload Logic (after all outputs and variables are defined) ---
    start_s3 = time.time()
    s3_folder = temp_dir_name  # Use the same provider-prefixed folder name for S3
    
    # Prepare files for parallel upload
    files_to_upload = {}
    for root, dirs, files in os.walk(temp_upload_folder):
        for fname in files:
            if fname.startswith('.'):
                continue  # skip hidden files like .DS_Store
            local_path = os.path.join(root, fname)
            # Store file path for parallel upload
            files_to_upload[fname] = local_path
    
    # Use parallel upload function instead of sequential uploads
    uploaded_files = parallel_upload_to_s3(files_to_upload, s3_folder)
    uploaded_files['s3_folder'] = s3_folder
    timings['s3_upload'] = time.time() - start_s3

    try:
        if base_names:
            # Map file extensions to S3 URLs for diagram_files
            urls = {}
            for base in base_names:
                for ext in output_formats:
                    fname = f"{base}.{ext}"
                    if fname in uploaded_files:
                        urls[ext] = uploaded_files[fname]
            # Use S3 URLs for code and markdown files
            raw_code_url = uploaded_files.get('generated_diagram_raw.py')
            sanitized_code_url = uploaded_files.get('generated_diagram.py')
            explanation_md_url = uploaded_files.get('generated_diagram.md')
            
            # Get URLs for input files if they exist
            original_input_url = uploaded_files.get('original_input.txt')
            rewritten_input_url = uploaded_files.get('rewritten_input.txt')
            
            timings['total'] = time.time() - start_total
            
            # Prepare response dictionary
            response_data = {
                'diagram_files': urls,  # S3 URLs for images and outputs
                'raw_code_url': raw_code_url,
                'sanitized_code_url': sanitized_code_url,
                'explanation': explanation,
                'explanation_md_url': explanation_md_url,
                'uploaded_files': uploaded_files  # all S3 URLs for all files
            }
            
            # Add input URLs if they exist
            if original_input_url:
                response_data['original_input_url'] = original_input_url
            if rewritten_input_url:
                response_data['rewritten_input_url'] = rewritten_input_url
                
            # Return the response
            return jsonify(response_data)

        # Final fallback: should never be reached, but ensures a response is always sent
        return error_response('Unknown server error', 500)
    finally:
        # Lambda automatically cleans up the /tmp directory between invocations
        pass

def upload_file_to_s3(local_path, s3_folder, filename):
    s3_key = f"{s3_folder}/{filename}"
    
    # Set optimal S3 upload parameters based on file size
    file_size = os.path.getsize(local_path)
    config = None
    
    # For larger files, use optimized transfer configuration
    if file_size > 1024 * 1024:  # 1MB
        config = boto3.s3.transfer.TransferConfig(
            multipart_threshold=1024 * 1024 * 5,  # 5MB
            max_concurrency=5,
            use_threads=True
        )
    
    try:
        # Use transfer with retry logic for reliability
        s3_client.upload_file(local_path, S3_BUCKET, s3_key, Config=config)
        # No need to delete local files as Lambda automatically cleans up /tmp
        return s3_key
    except Exception as e:
        print(f"Error uploading {filename}: {str(e)}")
        # Retry once with exponential backoff
        try:
            time.sleep(0.5)
            s3_client.upload_file(local_path, S3_BUCKET, s3_key, Config=config)
            return s3_key
        except Exception as retry_e:
            print(f"Retry failed for {filename}: {str(retry_e)}")
            return None

def parallel_upload_to_s3(files_to_upload, s3_folder):
    """Upload multiple files to S3 in parallel with optimized performance"""
    uploaded_files = {}
    
    # Define a worker function for the thread pool
    def upload_worker(file_info):
        local_path, filename = file_info
        try:
            s3_key = upload_file_to_s3(local_path, s3_folder, filename)
            if s3_key:
                url = generate_presigned_url(s3_key)
                return filename, url
            return filename, None
        except Exception as e:
            print(f"Error uploading {filename}: {str(e)}")
            return filename, None
    
    # Calculate optimal number of workers based on file count
    file_count = len(files_to_upload)
    max_workers = min(20, max(file_count, 5))  # Between 5-20 workers
    
    # Use a thread pool to upload files in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Group files by size to prioritize smaller files first
        small_files = {}
        large_files = {}
        
        for fname, local_path in files_to_upload.items():
            if os.path.getsize(local_path) < 1024 * 1024:  # 1MB
                small_files[fname] = local_path
            else:
                large_files[fname] = local_path
        
        # Submit small files first
        future_to_file = {
            executor.submit(upload_worker, (local_path, fname)): fname
            for fname, local_path in small_files.items()
        }
        
        # Add large files to the queue
        future_to_file.update({
            executor.submit(upload_worker, (local_path, fname)): fname
            for fname, local_path in large_files.items()
        })
        
        # Collect results as they complete
        for future in concurrent.futures.as_completed(future_to_file):
            filename, url = future.result()
            if url:
                uploaded_files[filename] = url
                
    return uploaded_files

def generate_presigned_url(s3_key, expires_in=3600):
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET, 'Key': s3_key},
            ExpiresIn=expires_in
        )
        return url
    except ClientError as e:
        print(f"Failed to generate presigned URL for {s3_key}: {e}")
        return None

# New endpoint: Rewrite user input based on cloud provider
@app.route('/rewrite', methods=['POST'])
def rewrite_endpoint():
    # Parse and validate the request
    data = request.get_json()
    if not data:
        return error_response('Invalid JSON in request body', 400)

    # Extract and validate user_input
    user_input = data.get('user_input')
    if not user_input or not isinstance(user_input, str) or not user_input.strip():
        return error_response('user_input is required and must be a non-empty string', 400)
    
    # Extract and validate provider
    provider = data.get('provider', '').lower()
    if not provider or provider not in ['aws', 'azure', 'gcp']:
        return error_response('Cloud provider is required. Please set provider to aws, azure, or gcp.', 400)

    # Map providers to rewrite instruction files
    provider_map = {
        'aws': 'instructions/rewrite/instructions_aws_rewrite.md',
        'azure': 'instructions/rewrite/instructions_azure_rewrite.md',
        'gcp': 'instructions/rewrite/instructions_gcp_rewrite.md'
    }
    
    instructions_file = provider_map.get(provider)
    
    # Verify the instructions file exists
    if not os.path.exists(instructions_file):
        return error_response(f'Rewrite instructions file not found at {instructions_file}. Please check your installation.', 500)
    
    # Read the instructions
    try:
        with open(instructions_file, 'r') as f:
            instructions = f.read()
    except Exception as e:
        return error_response(f'Failed to read {instructions_file}: {e}', 500)
    
    # Generate rewritten content with OpenAI
    try:
        rewritten_content = generate_rewrite_openai(user_input, instructions)
    except Exception as e:
        tb = traceback.format_exc()
        if ((hasattr(e, 'status_code') and e.status_code == 429) or 'quota' in str(e).lower() or 'rate limit' in str(e).lower()):
            return error_response(
                'OpenAI API quota exceeded. Please check your plan and billing at https://platform.openai.com/account/usage',
                429
            )
        return error_response(f'OpenAI API error: {str(e)}', 500, traceback=tb)
    
    # Return the rewritten content
    return jsonify({
        'rewritten_content': rewritten_content,
        'provider': provider
    })

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5050)
