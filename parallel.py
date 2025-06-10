import os
import time
import concurrent.futures
from llm_providers import generate_explanation_openai, generate_rewrite_openai

# Cache to store pre-loaded instruction files
_instruction_cache = {}

# Function to load rewrite instructions - cached to avoid repeated file I/O
def load_rewrite_instructions(provider):
    """Load the rewrite instructions for a provider from a cached version or disk"""
    if provider in _instruction_cache:
        return _instruction_cache[provider]
        
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
            _instruction_cache[provider] = rewrite_instructions
            return rewrite_instructions
    
    return None

# Function to prepare the explanation prompt with or without rewriting
def prepare_explanation_prompt(code, provider):
    """Create a prompt for explanation, either with provider-specific terminology or generic"""
    # Original explanation prompt - use this as fallback
    original_explanation_prompt = (
        "Given the following diagrams Python code, provide a short, detailed, bullet-point explanation "
        "of the flow and architecture. Be concise but clear. Do not exceed 8 bullet points.\n\n"
        "Code:\n"
        f"{code}"
    )
    
    # If no provider or provider not supported, return the original prompt
    if not provider or provider not in ['aws', 'azure', 'gcp']:
        return original_explanation_prompt
        
    # Try to get provider-specific rewrite instructions
    rewrite_instructions = load_rewrite_instructions(provider)
    if not rewrite_instructions:
        return original_explanation_prompt
        
    # Craft a provider-specific explanation prompt
    rewrite_prompt = (
        f"I need to explain this {provider.upper()} architecture diagram code in the correct terminology. "
        f"Please provide a bullet-point explanation using proper {provider.upper()} terminology for this code:\n\n{code}"
    )
    
    return {
        'original_prompt': original_explanation_prompt,
        'rewrite_prompt': rewrite_prompt,
        'rewrite_instructions': rewrite_instructions
    }

def perform_explanation_rewrite(prompt_data):
    """Rewrite the explanation prompt using provider-specific terminology"""
    try:
        # Extract data from the prompt_data dictionary
        rewrite_prompt = prompt_data['rewrite_prompt']
        rewrite_instructions = prompt_data['rewrite_instructions']
        
        # Rewrite the prompt using OpenAI
        rewritten_prompt = generate_rewrite_openai(rewrite_prompt, rewrite_instructions)
        return rewritten_prompt
    except Exception as e:
        print(f"Warning: Explanation prompt rewriting failed: {str(e)}. Will use original prompt.")
        return None

def generate_explanation(prompt):
    """Generate an explanation given a prompt"""
    return generate_explanation_openai(prompt)

# Function to generate explanation in a separate thread with improved parallelism
def generate_explanation_async(code, provider):
    """Generate an explanation asynchronously, using a ThreadPoolExecutor for true parallelism"""
    try:
        # Prepare the prompt data
        prompt_data = prepare_explanation_prompt(code, provider)
        
        # If we got a simple string, it's the original prompt without rewriting
        if isinstance(prompt_data, str):
            return generate_explanation(prompt_data)
            
        # For provider-specific explanations, we need to parallelize the rewrite and explanation
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            # Submit tasks for rewriting and generating with original prompt simultaneously
            rewrite_future = executor.submit(perform_explanation_rewrite, prompt_data)
            original_explanation_future = executor.submit(generate_explanation, prompt_data['original_prompt'])
            
            # Wait for the rewrite to complete with a timeout
            try:
                # Give the rewrite operation 15 seconds to complete
                rewritten_prompt = rewrite_future.result(timeout=15)
                
                # If we got a rewritten prompt, use it
                if rewritten_prompt:
                    # Cancel the original explanation if it's still running
                    if not original_explanation_future.done():
                        original_explanation_future.cancel()
                    
                    # Generate an explanation with the rewritten prompt
                    return generate_explanation(rewritten_prompt)
            except concurrent.futures.TimeoutError:
                print(f"Rewrite timed out, falling back to original explanation")
                
            # If we reach here, either rewrite failed or timed out, so use the original explanation
            return original_explanation_future.result()
    except Exception as e:
        print(f"Error in generate_explanation_async: {str(e)}")
        # Try a fallback direct explanation as a last resort
        try:
            fallback_prompt = (
                "Given the following diagrams Python code, provide a short, bullet-point explanation "
                "of the architecture. Be concise.\n\n"
                f"{code}"
            )
            return generate_explanation_openai(fallback_prompt)
        except Exception as fallback_e:
            print(f"Fallback explanation also failed: {str(fallback_e)}")
            return "Unable to generate explanation due to an error."
