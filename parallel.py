import os
import concurrent.futures
from llm_providers import generate_explanation_openai, generate_rewrite_openai

# Function to prepare the explanation prompt with or without rewriting
def prepare_explanation_prompt(code, provider):
    # Original explanation prompt
    original_explanation_prompt = (
        "Given the following diagrams Python code, provide a short, detailed, bullet-point explanation "
        "of the flow and architecture. Be concise but clear. Do not exceed 8 bullet points.\n\n"
        "Code:\n"
        f"{code}"
    )
    
    explanation_prompt = original_explanation_prompt
    
    # If we have a provider, try to rewrite the explanation prompt with provider-specific terminology
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
                    explanation_prompt = rewritten_prompt
        except Exception as e:
            # If rewriting fails, continue with the original explanation prompt
            print(f"Warning: Explanation prompt rewriting failed: {str(e)}. Continuing with original prompt.")
    
    return explanation_prompt

# Function to generate explanation in a separate thread
def generate_explanation_async(code, provider):
    try:
        # Prepare the explanation prompt (with rewriting if applicable)
        explanation_prompt = prepare_explanation_prompt(code, provider)
        
        # Generate the explanation
        explanation = generate_explanation_openai(explanation_prompt)
        return explanation
    except Exception as e:
        print(f"Error generating explanation: {str(e)}")
        return None
