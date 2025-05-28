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
# CONSTANTS AND UTILITY CLASSES
# =============================================================================

# Constants for input property names in MCP tool definitions
# These define the expected property names for inputs to MCP tools
_SNIPPET_NAME_PROPERTY_NAME = "snippetname"  # Property name for the snippet identifier
_SNIPPET_PROPERTY_NAME = "snippet"           # Property name for the snippet content
_PROJECT_ID_PROPERTY_NAME = "projectid"      # Property name for the project identifier
_CHAT_HISTORY_PROPERTY_NAME = "chathistory"  # Property name for previous chat context
_USER_QUERY_PROPERTY_NAME = "userquery"      # Property name for the user's specific question

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

# Properties for the save_snippet tool
# This tool saves code snippets with their vector embeddings
tool_properties_save_snippets = [
    ToolProperty(_SNIPPET_NAME_PROPERTY_NAME, "string", "A unique name or identifier for the code snippet. Provide this if you have a specific name for the snippet being saved. Essential for identifying the snippet later."),
    ToolProperty(_PROJECT_ID_PROPERTY_NAME, "string", "An identifier for a project to associate this snippet with. Useful for organizing snippets. If omitted or not relevant, it defaults to 'default-project'."),
    ToolProperty(_SNIPPET_PROPERTY_NAME, "string", "The actual code or text content of the snippet. Provide the content that needs to be saved and made searchable."),
]

# Properties for the get_snippet tool
# This tool retrieves previously saved snippets by name
tool_properties_get_snippets = [
    ToolProperty(_SNIPPET_NAME_PROPERTY_NAME, "string", "The unique name or identifier of the code snippet you want to retrieve. This is required to fetch a specific snippet."),
]

# Properties for the deep_wiki tool
# This tool generates comprehensive documentation from code snippets
tool_properties_wiki = [
    ToolProperty(_CHAT_HISTORY_PROPERTY_NAME, "string", "Optional. The preceding conversation history (e.g., user prompts and AI responses). Providing this helps contextualize the wiki content generation. Omit if no relevant history exists or if a general wiki is desired."),
    ToolProperty(_USER_QUERY_PROPERTY_NAME, "string", "Optional. The user's specific question, instruction, or topic to focus the wiki documentation on. If omitted, a general wiki covering available snippets might be generated."),
]

# Properties for the code_style tool
# This tool generates coding style guides based on existing snippets
tool_properties_code_style = [
    ToolProperty(_CHAT_HISTORY_PROPERTY_NAME, "string", "Optional. The preceding conversation history (e.g., user prompts and AI responses). This can provide context for the code style analysis or guide generation. Omit if not available or not relevant."),
    ToolProperty(_USER_QUERY_PROPERTY_NAME, "string", "Optional. The user's specific question, instruction, or prompt related to code style. If omitted, a general code style analysis or a default guide might be generated."),
]

# Convert tool properties to JSON for MCP tool registration
# This is required format for the MCP tool trigger binding
tool_properties_save_snippets_json = json.dumps([prop.to_dict() for prop in tool_properties_save_snippets])
tool_properties_get_snippets_json = json.dumps([prop.to_dict() for prop in tool_properties_get_snippets])
tool_properties_wiki_json = json.dumps([prop.to_dict() for prop in tool_properties_wiki])
tool_properties_code_style_json = json.dumps([prop.to_dict() for prop in tool_properties_code_style])

# =============================================================================
# SAVE SNIPPET FUNCTIONALITY
# =============================================================================

# HTTP endpoint for saving snippets
# This is accessible via standard HTTP POST requests
@app.route(route="snippets", methods=["POST"], auth_level=func.AuthLevel.FUNCTION)
@app.embeddings_input(arg_name="embeddings", input="{code}", input_type="rawText", embeddings_model="%EMBEDDING_MODEL_DEPLOYMENT_NAME%")
async def http_save_snippet(req: func.HttpRequest, embeddings: str) -> func.HttpResponse:
    """
    HTTP trigger function to save a code snippet with its vector embedding.
    
    Key features:
    - Takes a JSON payload with 'name', 'code', and optional 'projectId'
    - Uses Azure OpenAI to automatically generate vector embeddings
    - Stores the snippet and its embedding in Cosmos DB
    
    The @app.embeddings_input decorator:
    - Automatically calls Azure OpenAI before the function runs
    - Extracts 'code' from the request body
    - Generates a vector embedding for that code
    - Provides the embedding to the function via the 'embeddings' parameter
    """
    try:
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
        
        # 2. Extract the snippet details from the request
        project_id = req_body.get("projectId", "default-project")  # Use default if not provided
        name = req_body["name"]
        code = req_body["code"]

        # 3. Log some details about the snippet being saved
        logging.info(f"Input text length: {len(code)} characters")
        logging.info(f"Input text preview: {code[:100]}...")
        
        try:
            # 4. Process the embeddings generated by Azure OpenAI
            # The embeddings are provided as a JSON string that needs to be parsed
            embeddings_data = json.loads(embeddings)
            
            # 5. Extract the actual vector from the embeddings response
            # This is the numerical representation of the code's meaning
            embedding_vector = embeddings_data["response"]["data"][0]["embedding"]
            
            # 6. Save the snippet and its embedding to Cosmos DB
            result = await cosmos_ops.upsert_document(
                name=name,
                project_id=project_id,
                code=code,
                embedding=embedding_vector
            )
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            # Handle errors in embedding processing
            logging.error(f"Embeddings processing error: {str(e)}")
            return func.HttpResponse(
                body=json.dumps({"error": "Invalid embeddings data or structure"}),
                mimetype="application/json",
                status_code=500)
        
        # 7. Return success response with the result from Cosmos DB
        return func.HttpResponse(body=json.dumps(result), mimetype="application/json", status_code=200)
    except Exception as e:
        # General error handling
        logging.error(f"Error in http_save_snippet: {str(e)}")
        return func.HttpResponse(body=json.dumps({"error": str(e)}), mimetype="application/json", status_code=500)

# MCP tool for saving snippets
# This is accessible to AI assistants via the MCP protocol
@app.generic_trigger(
    arg_name="context",
    type="mcpToolTrigger",
    toolName="save_snippet",
    description="Saves a given code snippet. It can take a snippet name, the snippet content, and an optional project ID. Embeddings are generated for the content to enable semantic search. The LLM should provide 'snippetname' and 'snippet' when intending to save.",
    toolProperties=tool_properties_save_snippets_json,
)
@app.embeddings_input(arg_name="embeddings", input="{arguments.snippet}", input_type="rawText", embeddings_model="%EMBEDDING_MODEL_DEPLOYMENT_NAME%")
async def mcp_save_snippet(context: str, embeddings: str) -> str:
    """
    MCP tool to save a code snippet with vector embedding.
    
    Key features:
    - Receives parameters from an AI assistant like GitHub Copilot
    - Uses the same embedding generation as the HTTP endpoint
    - Shares the same storage logic with the HTTP endpoint
    
    The difference from the HTTP endpoint:
    - Receives parameters via the 'context' JSON string instead of HTTP body
    - Returns results as a JSON string instead of an HTTP response
    - Uses {arguments.snippet} in the embeddings_input decorator to reference
      the snippet content from the context arguments
    """
    try:
        # 1. Parse the context JSON string to extract the arguments
        mcp_data = json.loads(context)
        args = mcp_data.get("arguments", {})

        # 2. Extract snippet details from the arguments
        name = args.get(_SNIPPET_NAME_PROPERTY_NAME)  # Snippet name
        code = args.get(_SNIPPET_PROPERTY_NAME)       # Snippet content
        project_id = args.get(_PROJECT_ID_PROPERTY_NAME, "default-project")  # Use default if not provided

        # 3. Validate required parameters
        if not name or not code:
            missing_fields = []
            if not name: missing_fields.append(_SNIPPET_NAME_PROPERTY_NAME)
            if not code: missing_fields.append(_SNIPPET_PROPERTY_NAME)
            return json.dumps({"error": f"Missing essential arguments for save_snippet: {', '.join(missing_fields)}. Please provide both snippet name and content."})

        # 4. Log some details about the snippet being saved
        logging.info(f"Input text length: {len(code)} characters")
        logging.info(f"Input text preview: {code[:100]}...")
        
        try:
            # 5. Process the embeddings generated by Azure OpenAI
            embeddings_data = json.loads(embeddings)
            
            # 6. Extract the vector from the embeddings response
            embedding_vector = embeddings_data["response"]["data"][0]["embedding"]
            
            # 7. Save the snippet and its embedding to Cosmos DB
            # Uses the same storage function as the HTTP endpoint
            result = await cosmos_ops.upsert_document(name=name, project_id=project_id, code=code, embedding=embedding_vector)
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            # Handle errors in embedding processing
            logging.error(f"Embeddings processing error: {str(e)}")
            return json.dumps({"error": "Invalid embeddings data or structure"})
        
        # 8. Return success result as a JSON string
        return json.dumps(result)
    except json.JSONDecodeError:
        # Handle invalid context JSON
        return json.dumps({"error": "Invalid JSON received in context"})
    except Exception as e: 
        # General error handling
        logging.error(f"Error in mcp_save_snippet: {str(e)}")
        return json.dumps({"error": str(e)})

# =============================================================================
# GET SNIPPET FUNCTIONALITY
# =============================================================================

# HTTP endpoint for retrieving snippets
# This is accessible via standard HTTP GET requests
@app.route(route="snippets/{name}", methods=["GET"], auth_level=func.AuthLevel.FUNCTION)
async def http_get_snippet(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP trigger function to retrieve a code snippet by name.
    
    Key features:
    - Takes the snippet name from the URL path parameter
    - Retrieves the snippet from Cosmos DB
    - Returns the snippet as a JSON response
    
    No embedding generation is needed for retrieval by name.
    """
    try:
        # 1. Extract the snippet name from the route parameters
        name = req.route_params.get("name")
        if not name:
            # Return a 400 Bad Request if the name is missing
            return func.HttpResponse(body=json.dumps({"error": "Missing snippet name in route"}), mimetype="application/json", status_code=400)
        
        # 2. Retrieve the snippet from Cosmos DB
        snippet = await cosmos_ops.get_snippet_by_id(name)
        if not snippet:
            # Return a 404 Not Found if the snippet doesn't exist
            return func.HttpResponse(body=json.dumps({"error": f"Snippet '{name}' not found"}), mimetype="application/json", status_code=404)
        
        # 3. Return the snippet as a JSON response
        return func.HttpResponse(body=json.dumps(snippet), mimetype="application/json", status_code=200)
    except Exception as e:
        # General error handling
        logging.error(f"Error in http_get_snippet: {str(e)}")
        return func.HttpResponse(body=json.dumps({"error": str(e)}), mimetype="application/json", status_code=500)

# MCP tool for retrieving snippets
# This is accessible to AI assistants via the MCP protocol
@app.generic_trigger(
    arg_name="context",
    type="mcpToolTrigger",
    toolName="get_snippet",
    description="Retrieves a previously saved code snippet using its unique name. The LLM should provide the 'snippetname' when it intends to fetch a specific snippet.",
    toolProperties=tool_properties_get_snippets_json,
)
async def mcp_get_snippet(context) -> str:
    """
    MCP tool to retrieve a code snippet by name.
    
    Key features:
    - Receives the snippet name from an AI assistant
    - Uses the same retrieval logic as the HTTP endpoint
    - Returns the snippet as a JSON string
    
    The difference from the HTTP endpoint:
    - Receives the snippet name via the 'context' JSON string instead of URL path
    - Returns results as a JSON string instead of an HTTP response
    """
    try:
        # 1. Parse the context JSON string to extract the arguments
        mcp_data = json.loads(context)
        args = mcp_data.get("arguments", {})
        
        # 2. Extract the snippet name from the arguments
        name = args.get(_SNIPPET_NAME_PROPERTY_NAME)

        # 3. Validate the required parameter
        if not name:
            return json.dumps({"error": f"Missing essential argument for get_snippet: {_SNIPPET_NAME_PROPERTY_NAME}. Please provide the snippet name to retrieve."})
        
        # 4. Retrieve the snippet from Cosmos DB
        # Uses the same storage function as the HTTP endpoint
        snippet = await cosmos_ops.get_snippet_by_id(name)
        if not snippet:
            # Return an error if the snippet doesn't exist
            return json.dumps({"error": f"Snippet '{name}' not found"})
        
        # 5. Return the snippet as a JSON string
        return json.dumps(snippet)
    except json.JSONDecodeError:
        # Handle invalid context JSON
        return json.dumps({"error": "Invalid JSON received in context"})
    except Exception as e:
        # General error handling
        logging.error(f"Error in mcp_get_snippet: {str(e)}")
        return json.dumps({"error": str(e)})

# =============================================================================
# DEEP WIKI FUNCTIONALITY
# =============================================================================

# HTTP endpoint for generating comprehensive wiki documentation
# This is accessible via standard HTTP POST requests
@app.route(route="snippets/wiki", methods=["POST"], auth_level=func.AuthLevel.FUNCTION)
async def http_deep_wiki(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP trigger to generate architecture Diagram
    
    Key features:
    - Takes optional chat history and user query from the request body
    - Uses AI to analyze saved code snippets
    - Generates detailed documentation as markdown content
    
    This creates interconnected documentation that explains the code snippets
    and their relationships, suitable for creating a developer wiki.
    """
    try:
        logging.info("HTTP: Starting deep wiki content generation")
        
        # 1. Extract the request body, defaulting to an empty object if not provided
        req_body = req.get_json() if req.get_body() else {} 
        
        # 2. Extract optional parameters from the request
        chat_history = req_body.get("chatHistory", "")  # Previous conversation for context
        user_query = req_body.get("userQuery", "")      # Specific user question or focus
        
        # 3. Generate the wiki documentation using the AI agent
        # This will analyze saved snippets and generate appropriate content
        wiki_content = await deep_wiki.generate_deep_wiki(
            chat_history=chat_history,
            user_query=user_query
        )
        logging.info("HTTP: Successfully generated deep wiki content")
        
        # 4. Return the generated content as markdown
        # Note the mimetype is text/markdown, not application/json
        return func.HttpResponse(body=wiki_content, mimetype="text/markdown", status_code=200)
    except Exception as e:
        # General error handling
        logging.error(f"Error in http_deep_wiki: {str(e)}")
        return func.HttpResponse(body=json.dumps({"error": str(e)}), mimetype="application/json", status_code=500)

# MCP tool for generating comprehensive wiki documentation
# This is accessible to AI assistants via the MCP protocol
@app.generic_trigger(
    arg_name="context",
    type="mcpToolTrigger",
    toolName="deep_wiki",
    description="Creates comprehensive 'deep wiki' documentation. This involves generating content for a new wiki file (e.g., 'deep-wiki.md' to be placed in the workspace root), often by analyzing existing code snippets. Optional 'chathistory' and 'userquery' can be provided to refine or focus the wiki content; omit them for a general wiki.",
    toolProperties=tool_properties_wiki_json,
)
async def mcp_deep_wiki(context) -> str:
    """
    MCP tool to generate comprehensive wiki documentation based on saved snippets.
    
    Key features:
    - Receives optional parameters from an AI assistant
    - Uses the same AI agent as the HTTP endpoint
    - Returns the generated content as a markdown string
    
    The difference from the HTTP endpoint:
    - Receives parameters via the 'context' JSON string instead of HTTP body
    - Returns results directly as a markdown string, not wrapped in JSON
      (This is an exception to the usual pattern of returning JSON)
    """
    try:
        logging.info("MCP: Starting deep wiki content generation")
        
        # 1. Parse the context JSON string to extract the arguments
        mcp_data = json.loads(context)
        args = mcp_data.get("arguments", {})

        # 2. Extract optional parameters from the arguments
        chat_history = args.get(_CHAT_HISTORY_PROPERTY_NAME, "")  # Previous conversation for context
        user_query = args.get(_USER_QUERY_PROPERTY_NAME, "")      # Specific user question or focus
        
        # 3. Generate the wiki documentation using the AI agent
        # Uses the same function as the HTTP endpoint
        wiki_content = await deep_wiki.generate_deep_wiki(
            chat_history=chat_history,
            user_query=user_query
        )
        logging.info("MCP: Successfully generated deep wiki content")
        
        # 4. Return the raw markdown content
        # Note: Unlike other MCP tools, this returns raw markdown, not JSON
        return wiki_content 
    except json.JSONDecodeError:
        # Handle invalid context JSON
        return json.dumps({"error": "Invalid JSON received in context"})
    except Exception as e:
        # General error handling
        logging.error(f"Error in mcp_deep_wiki: {str(e)}")
        return json.dumps({"error": str(e)})