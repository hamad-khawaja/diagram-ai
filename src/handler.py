# =============================================================================
# AZURE FUNCTIONS APPLICATION WITH INTEGRATED AI SERVICES
# =============================================================================
#
# This application demonstrates a modern AI-powered code snippet manager built with:
#
# 1. Azure Functions - Serverless compute that runs your code in the cloud
#    - HTTP triggers - Standard RESTful API endpoints accessible over HTTP
#    - MCP triggers - Model Context Protocol for AI agent integration (e.g., GitHub Copilot)
#
#
# 3. Azure OpenAI - Provides AI models and embeddings
#    - Generates vector embeddings from code snippets
#    - These embeddings capture the semantic meaning of the code
#
# 4. Azure AI Agents - Specialized AI agents for code analysis
#    - For generating documentation and style guides from snippets
#
# The application provides two parallel interfaces for the same functionality:
# - HTTP endpoints for traditional API access
# - MCP tools for AI assistant integration

import json
import logging
import azure.functions as func
from data import cosmos_ops  # Module for Cosmos DB operations
from agents import deep_wiki, code_style  # Modules for AI agent operations

# Initialize the Azure Functions app
# This is the main entry point for all function definitions
app = func.FunctionApp()

# =============================================================================
# TODO: CONSTANTS AND UTILITY CLASSES
# =============================================================================

# Constants for input property names in MCP tool definitions
# These define the expected property names for inputs to MCP tools
_SNIPPET_NAME_PROPERTY_NAME = "snippetname"  # Property name for the snippet identifier
_SNIPPET_PROPERTY_NAME = "snippet"           # Property name for the snippet content
_PROJECT_ID_PROPERTY_NAME = "projectid"      # Property name for the project identifier
_CHAT_HISTORY_PROPERTY_NAME = "chathistory"  # Property name for previous chat context
_USER_QUERY_PROPERTY_NAME = "userquery"      #

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

    # 1. Extract and validate the request body
    req_body = req.get_json()
    required_fields = ["name", "code"]
    for field in required_fields:
        if field not in req_body:
            # Return a 400 Bad Request if required fields are missing
            return func.HttpResponse(
                body=json.dumps({"error": f"Missing required field: {field}"}),
                mimetype="application/json",
                status_code=400)
    
    # TODO - call the generate_diagram agent and return URL of the diagram

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