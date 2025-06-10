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
import threading
import queue

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

# Global explanation queue and result cache
# This allows for completely independent parallel processing of explanations
EXPLANATION_QUEUE = queue.Queue()
EXPLANATION_RESULTS = {}
EXPLANATION_EXECUTOR = concurrent.futures.ThreadPoolExecutor(max_workers=4, thread_name_prefix="explanation_worker")

# Configure S3 client with optimized settings
session = boto3.session.Session()
s3_client = session.client(
    's3',
    config=boto3.session.Config(
        signature_version='s3v4',
        retries={'max_attempts': 3, 'mode': 'standard'},
        max_pool_connections=50
    )
)

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
    # Include timing information if available
    if 'timings' in kwargs:
        # Format timing information
        timings = kwargs.get('timings', {})
        formatted_timings = {
            key: f"{value:.2f}s" for key, value in timings.items()
        }
        kwargs['performance'] = {'timings': formatted_timings}
        
        # Print performance data to console
        print("Performance Summary (Error Response):")
        print(f"Total execution time: {formatted_timings.get('total', 'N/A')}")
        for key, value in formatted_timings.items():
            if key != 'total':
                print(f"{key}: {value}")
                
        # Remove raw timing data from response
        kwargs.pop('timings', None)
    
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
    
    # Initialize detailed timing dictionary with all possible steps
    timings = {
        'start_time': time.time(),
        'request_processing': 0,
        'input_validation': 0,
        'description_rewriting': 0,
        'instruction_loading': 0,
        'llm': 0,
        'save_raw_code': 0,
        'save_inputs': 0,
        'code_sanitization': 0,
        'save_sanitized_code': 0,
        'temp_dir_creation': 0,
        'diagram_execution': 0,
        'explanation': 0,
        'file_collection': 0,
        's3_upload': 0,
        'response_preparation': 0,
        'total': 0,
        'unaccounted': 0  # Time not explicitly tracked by the steps above
    }
    
    # Track every step with timestamps for detailed analysis
    timestamps = {
        'start': time.time(),
        'steps': []
    }
    
    def record_step(step_name):
        now = time.time()
        timestamps['steps'].append({
            'step': step_name,
            'time': now,
            'elapsed_since_start': now - timestamps['start'],
            'elapsed_since_last': now - (timestamps['steps'][-1]['time'] if timestamps['steps'] else timestamps['start'])
        })
        
    record_step('start')
    start_total = time.time()
    start_request = time.time()

    # LLM code generation
    # Predefine code URLs for error handling
    raw_code_url = '/diagrams/generated_diagram_raw.py'
    sanitized_code_url = '/diagrams/generated_diagram.py'
    import re, subprocess, traceback, resource
    from diagrams_whitelist import is_code_whitelisted

    # Parse input data and validate
    record_step('parsing_request_start')
    start_input_validation = time.time()
    data = request.json
    description = data.get('description') if data else None
    timings['request_processing'] = time.time() - start_request
    record_step('parsing_request_end')

    if not isinstance(description, str) or not description.strip():
        timings['input_validation'] = time.time() - start_input_validation
        timings['total'] = time.time() - start_total
        return error_response('Description must be a non-empty string.', 400, timings=timings)
    if len(description) > 15000:
        timings['input_validation'] = time.time() - start_input_validation
        timings['total'] = time.time() - start_total
        return error_response('Description is too long (max 15000 chars).', 400, timings=timings)


    provider = data.get('provider') if data else None
    provider = provider.strip().lower() if provider else None
    if not provider:
        timings['input_validation'] = time.time() - start_input_validation
        timings['total'] = time.time() - start_total
        return error_response('No cloud provider specified. Please set provider to aws, azure, or gcp.', 400, timings=timings)

    timings['input_validation'] = time.time() - start_input_validation
    record_step('validation_complete')

    # First, run the description through the rewrite endpoint
    record_step('rewrite_start')
    start_rewrite = time.time()
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
    
    timings['description_rewriting'] = time.time() - start_rewrite
    record_step('rewrite_complete')

    # Map providers to instruction files in the /instructions/generate directory
    record_step('instruction_loading_start')
    start_instruction_loading = time.time()
    provider_map = {
        'aws': 'instructions/generate/instructions_aws_simplified.md',
        'azure': 'instructions/generate/instructions_azure_simplified.md',
        'gcp': 'instructions/generate/instructions_gcp_simplified.md'
    }
    provider_prefix = provider if provider in provider_map else 'unknown'
    instructions_file = provider_map.get(provider)
    if not instructions_file:
        timings['total'] = time.time() - start_total
        return error_response('Invalid provider. Please use aws, azure, or gcp.', 400, timings=timings)

    # Verify the instructions file exists
    if not os.path.exists(instructions_file):
        timings['total'] = time.time() - start_total
        return error_response(f'Instructions file not found at {instructions_file}. Please check your installation.', 500, timings=timings)


    try:
        with open(instructions_file, 'r') as f:
            instructions = f.read()
        timings['instruction_loading'] = time.time() - start_instruction_loading
        record_step('instruction_loading_complete')
    except Exception as e:
        timings['instruction_loading'] = time.time() - start_instruction_loading
        timings['total'] = time.time() - start_total
        record_step('instruction_loading_failed')
        return error_response(f'Failed to read {instructions_file}: {e}', 500, timings=timings)


    # Generate code with OpenAI
    record_step('llm_generation_start')
    start_llm = time.time()
    try:
        # Generate code using OpenAI
        code = generate_code_openai(description, instructions)
        record_step('llm_generation_complete')
    except Exception as e:
        tb = traceback.format_exc()
        timings['llm'] = time.time() - start_llm
        timings['total'] = time.time() - start_total
        record_step('llm_generation_failed')
        
        if ((hasattr(e, 'status_code') and e.status_code == 429) or 'quota' in str(e).lower() or 'rate limit' in str(e).lower()):
            return error_response(
                'OpenAI API quota exceeded. Please check your plan and billing at https://platform.openai.com/account/usage',
                429,
                raw_code_url=None,
                sanitized_code_url=None,
                timings=timings
            )
        return error_response(f'OpenAI API error: {str(e)}', 500, traceback=tb, timings=timings)
    timings['llm'] = time.time() - start_llm

    # Start explanation generation in a completely separate background process
    # This allows it to run independently from the main flow
    record_step('parallel_explanation_start')
    start_explanation = time.time()
    # Submit the explanation job to the background worker
    explanation_job_id = submit_explanation_job(code, provider)
    print(f"Submitted explanation job {explanation_job_id} to background worker")

    # Check for non-code or fallback LLM responses
    if code.strip().lower().startswith("sorry") or not ("import" in code or "with Diagram" in code):
        user_msg = code.strip().splitlines()[0] if code.strip() else "The model could not generate valid code for your request."
        timings['total'] = time.time() - start_total
        return error_response(f"The model could not generate valid code for your request: {user_msg}", 422, timings=timings)

    # --- Per-request temp directory, prefixed by provider ---
    record_step('temp_dir_creation_start')
    start_temp_dir = time.time()
    import tempfile, shutil
    temp_uuid = str(uuid.uuid4())
    temp_dir_name = f"{provider_prefix}-{temp_uuid}"
    
    # Create a Lambda-safe path using our helper function
    temp_upload_folder = get_lambda_safe_path(os.path.join('diagrams', temp_dir_name))
    os.makedirs(temp_upload_folder, exist_ok=True)
    timings['temp_dir_creation'] = time.time() - start_temp_dir
    record_step('temp_dir_creation_complete')

    # Save raw code
    record_step('save_raw_code_start')
    start_save_raw = time.time()
    raw_code_path = os.path.join(temp_upload_folder, 'generated_diagram_raw.py')
    try:
        with open(raw_code_path, 'w') as f:
            f.write(code)
        # Logging removed
    except Exception as e:
        # No need to clean up as Lambda automatically cleans up /tmp
        timings['save_raw_code'] = time.time() - start_save_raw
        timings['total'] = time.time() - start_total
        record_step('save_raw_code_failed')
        return error_response('Failed to save raw code', 500, timings=timings)
    timings['save_raw_code'] = time.time() - start_save_raw
    record_step('save_raw_code_complete')

    # Save original and rewritten descriptions
    record_step('save_inputs_start')
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
    record_step('save_inputs_complete')

    # Sanitize code
    record_step('code_sanitization_start')
    start_sanitize = time.time()
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
    timings['code_sanitization'] = time.time() - start_sanitize
    record_step('code_sanitization_complete')

    # Save sanitized code before running it!
    record_step('save_sanitized_code_start')
    start_save_sanitized = time.time()
    sanitized_code_path = os.path.join(temp_upload_folder, 'generated_diagram.py')
    try:
        with open(sanitized_code_path, 'w') as f:
            f.write(code)
        # Logging removed
    except Exception as e:
        # No need to clean up as Lambda automatically cleans up /tmp
        timings['save_sanitized_code'] = time.time() - start_save_sanitized
        timings['total'] = time.time() - start_total
        record_step('save_sanitized_code_failed')
        return error_response('Failed to save sanitized code', 500, timings=timings)
    timings['save_sanitized_code'] = time.time() - start_save_sanitized
    record_step('save_sanitized_code_complete')

    # Run diagram code
    record_step('diagram_execution_start')
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
            timings['diagram_execution'] = time.time() - start_exec
            timings['total'] = time.time() - start_total
            
            # Shutdown the executor before returning on error
            
            # If it's a SyntaxError or the code is not valid Python, return 422
            if 'SyntaxError' in proc.stderr or 'invalid syntax' in proc.stderr:
                response_data = {
                    'error': 'Diagram code execution failed due to invalid or non-Python code.',
                    'stderr': proc.stderr,
                    'stdout': proc.stdout,
                    'raw_code_url': raw_code_url,
                    'sanitized_code_url': sanitized_code_url,
                    'performance': {
                        'timings': {key: f"{value:.2f}s" for key, value in timings.items()}
                    }
                }
                return jsonify(response_data), 422
            # If it's a TypeError for list >> list, return a user-friendly error
            if 'TypeError' in proc.stderr and 'unsupported operand type(s) for >>' in proc.stderr:
                response_data = {
                    'error': 'Diagram code execution failed: You cannot use >> between lists of nodes. Connect nodes individually or use a nested loop.',
                    'stderr': proc.stderr,
                    'stdout': proc.stdout,
                    'raw_code_url': raw_code_url,
                    'sanitized_code_url': sanitized_code_url,
                    'performance': {
                        'timings': {key: f"{value:.2f}s" for key, value in timings.items()}
                    }
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
                        'stdout': proc.stdout,
                        'performance': {
                            'timings': {key: f"{value:.2f}s" for key, value in timings.items()}
                        }
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
                        'stdout': proc.stdout,
                        'performance': {
                            'timings': {key: f"{value:.2f}s" for key, value in timings.items()}
                        }
                    }
                    return jsonify(response_data), 206
            response_data = {
                'error': 'Diagram code execution failed',
                'stderr': proc.stderr,
                'stdout': proc.stdout,
                'raw_code_url': raw_code_url,
                'sanitized_code_url': sanitized_code_url,
                'performance': {
                    'timings': {key: f"{value:.2f}s" for key, value in timings.items()}
                }
            }
            return jsonify(response_data), 500
    except Exception as e:
        timings['diagram_execution'] = time.time() - start_exec
        timings['total'] = time.time() - start_total
        return error_response(f'Diagram execution error: {str(e)}', 500, timings=timings)
    finally:
        os.chdir(cwd)
        
    timings['diagram_execution'] = time.time() - start_exec
    record_step('diagram_execution_complete')
    
    # Now get the explanation result
    record_step('get_explanation_result_start')
    try:
        # Get the result from our background processing system with a short timeout
        # This should return immediately if the result is ready, or a placeholder if not
        explanation_result = get_explanation_result(explanation_job_id, timeout=0.5)
        explanation = explanation_result['result']
        
        if explanation_result['error'] == 'timeout':
            print(f"Explanation generation is still in progress (job {explanation_job_id})")
            record_step('get_explanation_result_pending')
        else:
            print(f"Got explanation result for job {explanation_job_id} (took {explanation_result['time_taken']:.2f}s)")
            record_step('get_explanation_result_complete')
    except Exception as e:
        print(f"Error getting explanation result: {str(e)}")
        explanation = f"Explanation generation failed: {str(e)}"
        record_step('get_explanation_result_failed')
        
    # Calculate explanation time from when we started it
    timings['explanation'] = time.time() - start_explanation
    record_step('parallel_explanation_complete')

    # Collect output files
    record_step('file_collection_start')
    start_file_collection = time.time()
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
        
    timings['file_collection'] = time.time() - start_file_collection
    record_step('file_collection_complete')

    # --- S3 Upload Logic (after all outputs and variables are defined) ---
    record_step('s3_upload_start')
    start_s3 = time.time()
    s3_folder = temp_dir_name  # Use the same provider-prefixed folder name for S3
    
    # Prepare files for parallel upload - use a more efficient approach
    files_to_upload = {}
    for root, dirs, files in os.walk(temp_upload_folder):
        for fname in files:
            if fname.startswith('.'):
                continue  # skip hidden files like .DS_Store
                
            # Get the full local path
            local_path = os.path.join(root, fname)
            
            # Calculate relative path from temp_upload_folder
            rel_path = os.path.relpath(local_path, temp_upload_folder)
            
            # For files directly in temp_upload_folder, use filename as key
            # For files in subdirectories, preserve their path
            upload_key = rel_path
            files_to_upload[upload_key] = local_path
    
    # Immediately start the upload process in parallel
    uploaded_files = parallel_upload_to_s3(files_to_upload, s3_folder)
    uploaded_files['s3_folder'] = s3_folder
    timings['s3_upload'] = time.time() - start_s3
    record_step('s3_upload_complete')

    # Prepare the response
    record_step('response_preparation_start')
    start_response_prep = time.time()
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
            
            # Calculate total execution time
            timings['total'] = time.time() - start_total
            
            # Calculate unaccounted time - time not explicitly measured by individual steps
            measured_time = 0
            for key, value in timings.items():
                if key not in ['total', 'unaccounted', 'start_time']:
                    measured_time += value
            timings['unaccounted'] = timings['total'] - measured_time
            
            # Format timing information for display
            formatted_timings = {
                key: f"{value:.2f}s" for key, value in timings.items()
            }
            
            # Add detailed step timestamps for debugging
            step_timing_analysis = []
            for i in range(1, len(timestamps['steps'])):
                prev_step = timestamps['steps'][i-1]
                curr_step = timestamps['steps'][i]
                step_timing_analysis.append({
                    'from': prev_step['step'],
                    'to': curr_step['step'],
                    'elapsed': f"{curr_step['time'] - prev_step['time']:.2f}s",
                    'cumulative': f"{curr_step['elapsed_since_start']:.2f}s"
                })
            
            # Add file counts and sizes for S3 upload analysis
            file_stats = {
                'file_count': len(files_to_upload),
                'total_size_mb': sum(os.path.getsize(path) for path in files_to_upload.values()) / (1024 * 1024),
                'upload_speed_mb_per_s': (sum(os.path.getsize(path) for path in files_to_upload.values()) / (1024 * 1024)) / timings['s3_upload'] if timings['s3_upload'] > 0 else 0
            }
            formatted_file_stats = {
                'file_count': file_stats['file_count'],
                'total_size_mb': f"{file_stats['total_size_mb']:.2f} MB",
                'upload_speed_mb_per_s': f"{file_stats['upload_speed_mb_per_s']:.2f} MB/s"
            }
            
            # Add URL generation stats if available
            url_gen_stats = uploaded_files.pop('__url_gen_stats', None)
            if url_gen_stats:
                formatted_file_stats['url_generation'] = url_gen_stats
            
            # Prepare response dictionary
            response_data = {
                'diagram_files': urls,  # S3 URLs for images and outputs
                'raw_code_url': raw_code_url,
                'sanitized_code_url': sanitized_code_url,
                'explanation': explanation,
                'explanation_md_url': explanation_md_url,
                'explanation_status': 'complete' if not (explanation and explanation.startswith("Explanation generation")) else 'pending',
                'uploaded_files': uploaded_files,  # all S3 URLs for all files
                'performance': {
                    'timings': formatted_timings,
                    'file_stats': formatted_file_stats,
                    'detailed_timing': step_timing_analysis
                }
            }
            
            timings['response_preparation'] = time.time() - start_response_prep
            record_step('response_preparation_complete')
            
            # Add input URLs if they exist
            if original_input_url:
                response_data['original_input_url'] = original_input_url
            if rewritten_input_url:
                response_data['rewritten_input_url'] = rewritten_input_url
                
            # Print performance data to console for monitoring
            print("\n------ Performance Summary ------")
            print(f"Total execution time: {formatted_timings['total']}")
            print(f"Unaccounted time: {formatted_timings['unaccounted']} ({(timings['unaccounted']/timings['total']*100):.1f}% of total)")
            print("\nMajor Operations:")
            print(f"  LLM generation time: {formatted_timings['llm']}")
            print(f"  Explanation generation time: {formatted_timings.get('explanation', 'N/A')}")
            print(f"  Diagram execution time: {formatted_timings.get('diagram_execution', 'N/A')}")
            print(f"  S3 upload time: {formatted_timings['s3_upload']} ({formatted_file_stats['file_count']} files, {formatted_file_stats['total_size_mb']}, {formatted_file_stats['upload_speed_mb_per_s']})")
            
            # Find the explanation-related steps for detailed analysis
            explanation_steps = []
            for step in step_timing_analysis:
                if 'explanation' in step['from'].lower() or 'explanation' in step['to'].lower():
                    explanation_steps.append(step)
            
            if explanation_steps:
                print("\nExplanation Generation Steps:")
                for step in explanation_steps:
                    print(f"  {step['from']} → {step['to']}: {step['elapsed']} (cumulative: {step['cumulative']})")
            
            if url_gen_stats:
                print(f"  Presigned URL generation: {url_gen_stats['total_time']} for {url_gen_stats['count']} URLs (avg: {url_gen_stats['avg_time']} per URL)")
            
            print("\nDetailed Step Timing:")
            for step in step_timing_analysis:
                print(f"  {step['from']} → {step['to']}: {step['elapsed']} (cumulative: {step['cumulative']})")
            
            print("\nAll Timing Data:")
            for key, value in sorted(formatted_timings.items()):
                if key not in ['total', 'unaccounted', 'start_time']:
                    print(f"  {key}: {value}")
            print("-------------------------------\n")
                
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
    start_time = time.time()
    
    # Track specific phases of the upload
    phases = {
        'prepare': 0,
        'upload': 0,
        'retry': 0,
        'total': 0
    }
    
    phase_start = time.time()
    
    # Use an optimized transfer config for all uploads
    # Lowering multipart_threshold to 1MB to use multipart uploads more often
    # Increasing max_concurrency for better parallelization
    config = boto3.s3.transfer.TransferConfig(
        multipart_threshold=1024 * 1024,  # 1MB
        max_concurrency=10,
        use_threads=True,
        max_io_queue=20
    )
    
    phases['prepare'] = time.time() - phase_start
    
    try:
        # Use transfer with retry logic for reliability
        phase_start = time.time()
        s3_client.upload_file(local_path, S3_BUCKET, s3_key, Config=config)
        phases['upload'] = time.time() - phase_start
        
        # Log upload time for large files
        upload_time = time.time() - start_time
        upload_speed = file_size / (upload_time * 1024 * 1024) if upload_time > 0 else 0
        if file_size > 1024 * 1024:  # Log only for files > 1MB
            print(f"Uploaded {filename} ({file_size/1024/1024:.2f} MB) in {upload_time:.2f}s ({upload_speed:.2f} MB/s)")
            
            # Log phase breakdown for large files
            phase_percents = {k: f"{v/upload_time*100:.1f}%" for k, v in phases.items() if k != 'total'}
            print(f"  Phases: {phase_percents}")
        
        # No need to delete local files as Lambda automatically cleans up /tmp
        phases['total'] = time.time() - start_time
        return s3_key
    except Exception as e:
        print(f"Error uploading {filename}: {str(e)}")
        # Retry with exponential backoff
        try:
            phase_start = time.time()
            time.sleep(0.5)
            s3_client.upload_file(local_path, S3_BUCKET, s3_key, Config=config)
            phases['retry'] = time.time() - phase_start
            
            upload_time = time.time() - start_time
            print(f"Retry succeeded for {filename} ({file_size/1024/1024:.2f} MB) in {upload_time:.2f}s")
            phases['total'] = upload_time
            return s3_key
        except Exception as retry_e:
            print(f"Retry failed for {filename}: {str(retry_e)}")
            return None

def parallel_upload_to_s3(files_to_upload, s3_folder):
    """Upload multiple files to S3 in parallel with optimized performance"""
    uploaded_files = {}
    
    # Track time spent generating presigned URLs
    url_gen_total_time = 0
    url_gen_count = 0
    
    # Define a worker function for the thread pool
    def upload_worker(file_info):
        nonlocal url_gen_total_time, url_gen_count
        local_path, filename = file_info
        try:
            # Time the S3 upload
            upload_start = time.time()
            s3_key = upload_file_to_s3(local_path, s3_folder, filename)
            upload_time = time.time() - upload_start
            
            if s3_key:
                # Time the presigned URL generation
                url_gen_start = time.time()
                url = generate_presigned_url(s3_key)
                url_gen_time = time.time() - url_gen_start
                
                # Track URL generation statistics
                url_gen_total_time += url_gen_time
                url_gen_count += 1
                
                return filename, url, upload_time, url_gen_time
            return filename, None, upload_time, 0
        except Exception as e:
            print(f"Error uploading {filename}: {str(e)}")
            return filename, None, 0, 0
    
    # Optimize the number of workers based on file count and system resources
    file_count = len(files_to_upload)
    # Use more workers for better parallelization, but cap at a reasonable limit
    max_workers = min(32, max(file_count, 10))
    
    # Sort files by priority to upload important files first
    priority_files = []
    normal_files = []
    
    for fname, local_path in files_to_upload.items():
        # Prioritize PNG files (main diagram output) and small files
        if fname.endswith('.png') or (os.path.getsize(local_path) < 100 * 1024):  # Less than 100KB
            priority_files.append((local_path, fname))
        else:
            normal_files.append((local_path, fname))
    
    # Combine lists with priority files first
    all_files = priority_files + normal_files
    
    # Use a thread pool to upload files in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all files for upload
        future_to_file = {
            executor.submit(upload_worker, file_info): file_info[1]  # filename is file_info[1]
            for file_info in all_files
        }
        
        # Process results as they complete
        for future in concurrent.futures.as_completed(future_to_file):
            filename, url, upload_time, url_gen_time = future.result()
            if url:
                uploaded_files[filename] = url
    
    # Add URL generation statistics to the result
    if url_gen_count > 0:
        avg_url_gen_time = url_gen_total_time / url_gen_count
        print(f"Presigned URL stats: generated {url_gen_count} URLs in {url_gen_total_time:.2f}s " +
              f"(avg: {avg_url_gen_time:.4f}s per URL, total: {url_gen_total_time:.2f}s)")
        
        # Add stats to the result dictionary
        uploaded_files['__url_gen_stats'] = {
            'count': url_gen_count,
            'total_time': f"{url_gen_total_time:.2f}s",
            'avg_time': f"{avg_url_gen_time:.4f}s"
        }
    
    return uploaded_files

def generate_presigned_url(s3_key, expires_in=3600):
    try:
        # Track time for generating the presigned URL
        url_gen_start = time.time()
        
        # Use a longer expiration time to reduce the need for regenerating URLs
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': S3_BUCKET, 
                'Key': s3_key,
                'ResponseContentDisposition': f'inline; filename="{os.path.basename(s3_key)}"'
            },
            ExpiresIn=expires_in
        )
        
        url_gen_time = time.time() - url_gen_start
        # Log if it's taking a long time (over 100ms)
        if url_gen_time > 0.1:
            print(f"Slow presigned URL generation for {s3_key}: {url_gen_time:.2f}s")
        
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

# Start background worker for explanation generation
def explanation_worker():
    """Background worker that processes explanation requests from the queue"""
    print("Starting explanation worker thread")
    while True:
        try:
            # Get a task from the queue with a timeout
            task = EXPLANATION_QUEUE.get(timeout=1)
            if task is None:  # Special signal to terminate
                break
                
            job_id, code, provider = task
            print(f"Processing explanation job {job_id}")
            start_time = time.time()
            
            try:
                # Generate the explanation
                explanation = generate_explanation_async(code, provider)
                
                # Store the result
                EXPLANATION_RESULTS[job_id] = {
                    'result': explanation,
                    'error': None,
                    'time_taken': time.time() - start_time
                }
                print(f"Completed explanation job {job_id} in {time.time() - start_time:.2f}s")
            except Exception as e:
                print(f"Error processing explanation job {job_id}: {str(e)}")
                EXPLANATION_RESULTS[job_id] = {
                    'result': None,
                    'error': str(e),
                    'time_taken': time.time() - start_time
                }
                
            # Mark task as done
            EXPLANATION_QUEUE.task_done()
        except queue.Empty:
            # No tasks in queue, continue polling
            continue
        except Exception as e:
            print(f"Error in explanation worker: {str(e)}")
            # Continue processing other jobs
            continue

# Start the worker thread
explanation_thread = threading.Thread(target=explanation_worker, daemon=True)
explanation_thread.start()

# Register a function to clean up background threads when the app exits
import atexit

@atexit.register
def cleanup_background_threads():
    """Clean up background threads when the app exits"""
    print("Shutting down background workers...")
    # Signal workers to terminate
    EXPLANATION_QUEUE.put(None)
    # Wait for workers to finish current tasks (up to 2 seconds)
    explanation_thread.join(timeout=2)
    # Shut down the thread pool
    EXPLANATION_EXECUTOR.shutdown(wait=False)
    print("Background workers shutdown complete")

# Function to submit a new explanation job
def submit_explanation_job(code, provider):
    """Submit a new explanation job to be processed in the background"""
    job_id = str(uuid.uuid4())
    EXPLANATION_QUEUE.put((job_id, code, provider))
    return job_id

# Function to get explanation result, with timeout
def get_explanation_result(job_id, timeout=5.0):
    """Get the result of an explanation job, with timeout"""
    start_wait = time.time()
    while (time.time() - start_wait) < timeout:
        if job_id in EXPLANATION_RESULTS:
            result = EXPLANATION_RESULTS.pop(job_id)  # Get and remove the result
            return result
        time.sleep(0.1)  # Short sleep to avoid CPU spinning
    
    # Timeout occurred
    return {
        'result': f"Explanation generation is taking longer than expected. Please check back later.",
        'error': "timeout",
        'time_taken': timeout
    }

# New endpoint: Check explanation status
@app.route('/check_explanation/<job_id>', methods=['GET'])
def check_explanation(job_id):
    """Check the status of a previously submitted explanation job"""
    # Get the result with a short timeout
    explanation_result = get_explanation_result(job_id, timeout=0.1)
    
    # Prepare the response
    if explanation_result['error'] == 'timeout':
        return jsonify({
            'status': 'pending',
            'message': 'Explanation is still being generated'
        })
    elif explanation_result['error']:
        return jsonify({
            'status': 'error',
            'message': f"Error generating explanation: {explanation_result['error']}",
            'time_taken': f"{explanation_result['time_taken']:.2f}s"
        }), 500
    else:
        return jsonify({
            'status': 'complete',
            'explanation': explanation_result['result'],
            'time_taken': f"{explanation_result['time_taken']:.2f}s"
        })

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5050)
