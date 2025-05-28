import os
import re
import json
import uuid
import logging
import traceback
import subprocess
import resource
from flask import request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import azure.functions as func
from agents import diagram
from diagrams_whitelist import is_code_whitelisted


# Initialize the Azure Functions app
# This is the main entry point for all function definitions
app = func.FunctionApp()

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

# =============================================================================
# TODO: CONSTANTS AND UTILITY CLASSES
# =============================================================================


# Utility class to define properties for MCP tools
# This creates a standardized way to document and validate expected inputs
class ToolProperty:
    """
    Defines a property for an MCP tool, including its name, data type, and description.
    
    These properties are used by AI assistants (like GitHub Copilot) to understand:
    - What inputs each tool expects
    - What data types those inputs should be
    - How to describe each input to users
    
    This helps the AI to correctly invoke the tool with appropriate parameters.
    """
    def __init__(self, property_name: str, property_type: str, description: str):
        self.propertyName = property_name    # Name of the property
        self.propertyType = property_type    # Data type (string, number, etc.)
        self.description = description       # Human-readable description
        
    def to_dict(self):
        """
        Converts the property definition to a dictionary format for JSON serialization.
        Required for MCP tool registration.
        """
        return {
            "propertyName": self.propertyName,
            "propertyType": self.propertyType,
            "description": self.description,
        }

# =============================================================================
# TOOL PROPERTY DEFINITIONS
# =============================================================================
# Each MCP tool needs a schema definition to describe its expected inputs
# This is how AI assistants know what parameters to provide when using these tools

# TODO

# =============================================================================
# generate_diagram FUNCTIONALITY
# =============================================================================

# HTTP endpoint for saving snippets
# This is accessible via standard HTTP POST requests
@app.route(route="generate", methods=["POST"], auth_level=func.AuthLevel.FUNCTION)
@app.embeddings_input(arg_name="embeddings", input="{code}", input_type="rawText", embeddings_model="%EMBEDDING_MODEL_DEPLOYMENT_NAME%")
async def generate_diagram(req: func.HttpRequest, embeddings: str) -> func.HttpResponse:
    """
    HTTP trigger function to save a code snippet with its vector embedding.
    
    The @app.embeddings_input decorator:
    - Automatically calls Azure OpenAI before the function runs
    - Extracts 'code' from the request body
    - Generates a vector embedding for that code
    - Provides the embedding to the function via the 'embeddings' parameter
    """

    # TODO - MOVE APP CODE HERE

# MCP tool for saving snippets
# This is accessible to AI assistants via the MCP protocol
@app.generic_trigger(
    arg_name="",
    type="",
    toolName="generate_diagram",
    description="S",
    toolProperties="",
)
@app.embeddings_input(arg_name="embeddings", input="{arguments.snippet}", input_type="rawText", embeddings_model="%EMBEDDING_MODEL_DEPLOYMENT_NAME%")
async def mcp_save_snippet(context: str, embeddings: str) -> str:
    """
    MCP tool to generate diagram.
    
    Key features:
    - Receives parameters from an AI assistant like GitHub Copilot
    - Uses the same embedding generation as the HTTP endpoint
    - Shares the same storage logic with the HTTP endpoint
    
    The difference from the HTTP endpoint:
    - Receives parameters via the 'context' JSON string instead of HTTP body
    - Returns results as a JSON string instead of an HTTP response
    """
    
    #TODO - call the generate_diagram agent and return URL of the diagram