from app import app
from mangum import Mangum
from asgiref.wsgi import WsgiToAsgi
import json
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

asgi_app = WsgiToAsgi(app)
mangum_handler = Mangum(asgi_app, lifespan="off")

def handler(event, context):
    # Log the entire event for debugging
    logger.info(f"Lambda event: {json.dumps(event)}")
    
    # Print key parts of the event
    if 'requestContext' in event and 'http' in event['requestContext']:
        method = event['requestContext']['http'].get('method', 'UNKNOWN')
        path = event['requestContext']['http'].get('path', 'UNKNOWN')
        logger.info(f"Request: {method} {path}")
    
    # Forward to Mangum handler
    try:
        response = mangum_handler(event, context)
        logger.info(f"Response status: {response.get('statusCode', 'UNKNOWN')}")
        return response
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        logger.error(f"Error in Lambda handler: {str(e)}\n{error_traceback}")
        return {
            "statusCode": 500,
            "headers": {
                "content-type": "application/json",
                "access-control-allow-origin": "*"
            },
            "body": json.dumps({
                "error": f"Internal server error: {str(e)}",
                "traceback": error_traceback
            })
        }
