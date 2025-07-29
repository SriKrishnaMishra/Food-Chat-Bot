from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import logging
import json
import os
import time
from typing import Dict, Any, Callable, List
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables first
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import custom modules after logging is configured
try:
    import db_helper
    import generic_helper
    logger.info("Successfully imported custom modules")
except ImportError as e:
    logger.error(f"Failed to import custom modules: {e}")
    raise

# Initialize FastAPI app
app = FastAPI(
    title="Pandeyji Eatery API",
    description="API for Pandeyji Eatery chatbot with web interface",
    version="1.0.0"
)

# Set up templates and static files
templates = Jinja2Templates(directory="templates")

# Mount static files if directory exists
if Path("static").exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Dictionary to store in-progress orders
inprogress_orders: Dict[str, Dict[str, int]] = {}

@app.get("/", response_class=HTMLResponse)
async def web_interface(request: Request):
    """Serve the web chat interface"""
    try:
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        logger.error(f"Error serving web interface: {e}")
        return HTMLResponse(content="""
        <html>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1>🍽️ Pandeyji Eatery</h1>
                <p>Chat interface is loading...</p>
                <p>API is running at <a href="/docs">/docs</a></p>
            </body>
        </html>
        """)

@app.get("/api", response_class=JSONResponse)
async def api_status():
    """API status endpoint"""
    return {
        "message": "Pandeyji Eatery API is running",
        "status": "healthy",
        "version": "1.0.0",
        "endpoints": {
            "web_interface": "GET /",
            "webhook": "POST /webhook", 
            "api_status": "GET /api",
            "docs": "GET /docs",
            "health": "GET /health"
        }
    }

@app.get("/health")
async def health_check():
    """Detailed health check endpoint"""
    # Test database connection
    db_status = "connected" if db_helper.cnx and db_helper.cnx.is_connected() else "disconnected"
    
    return {
        "status": "healthy",
        "database": db_status,
        "active_sessions": len(inprogress_orders),
        "timestamp": time.time()
    }

@app.post("/webhook")
async def handle_request(request: Request):
    """
    Main webhook endpoint for Dialogflow

    This function handles all incoming webhook requests from Dialogflow,
    extracts the intent and parameters, and routes to the appropriate handler.
    """
    try:
        # Retrieve the JSON data from the request
        payload = await request.json()
        logger.info(f"Received webhook request: {payload.get('queryResult', {}).get('intent', {}).get('displayName', 'Unknown intent')}")

        # Extract the necessary information from the payload
        # based on the structure of the WebhookRequest from Dialogflow
        query_result = payload.get('queryResult', {})
        intent = query_result.get('intent', {}).get('displayName', '')
        parameters = query_result.get('parameters', {})
        output_contexts = query_result.get('outputContexts', [])

        if not output_contexts:
            logger.error("No output contexts found in the request")
            return JSONResponse(content={
                "fulfillmentText": "I'm sorry, but I couldn't process your request. Please try again."
            })

        session_id = generic_helper.extract_session_id(output_contexts[0]["name"])

        if not session_id:
            logger.error("Failed to extract session ID from context")
            return JSONResponse(content={
                "fulfillmentText": "I'm sorry, but I couldn't identify your session. Please try again."
            })

        # Map intents to their handler functions
        intent_handler_dict = {
            'order.add - context: ongoing-order': add_to_order,
            'order.remove - context: ongoing-order': remove_from_order,
            'order.complete - context: ongoing-order': complete_order,
            'track.order - context: ongoing-tracking': track_order
        }

        # Check if the intent is supported
        if intent not in intent_handler_dict:
            logger.warning(f"Unsupported intent: {intent}")
            return JSONResponse(content={
                "fulfillmentText": "I'm sorry, I don't know how to process that request. Can you try something else?"
            })

        # Call the appropriate handler function
        logger.info(f"Routing to handler for intent: {intent}")
        return intent_handler_dict[intent](parameters, session_id)

    except Exception as e:
        logger.error(f"Error processing webhook request: {str(e)}", exc_info=True)
        return JSONResponse(content={
            "fulfillmentText": "I'm sorry, but something went wrong. Please try again later."
        })

def save_to_db(order: dict) -> int:
    """
    Save the order to the database

    Args:
        order: Dictionary with food items as keys and quantities as values

    Returns:
        int: The order ID if successful, -1 if there was an error
    """
    try:
        # Get the next available order ID
        next_order_id = db_helper.get_next_order_id()
        logger.info(f"Saving order with ID {next_order_id}: {order}")

        # Insert individual items along with quantity in orders table
        for food_item, quantity in order.items():
            rcode = db_helper.insert_order_item(
                food_item,
                quantity,
                next_order_id
            )

            if rcode == -1:
                logger.error(f"Failed to insert order item: {food_item}, quantity: {quantity}")
                return -1

        # Now insert order tracking status
        result = db_helper.insert_order_tracking(next_order_id, "in progress")
        if result == -1:
            logger.error(f"Failed to insert order tracking for order ID: {next_order_id}")
            return -1

        logger.info(f"Order {next_order_id} saved successfully")
        return next_order_id

    except Exception as e:
        logger.error(f"Error saving order to database: {str(e)}", exc_info=True)
        return -1

def complete_order(parameters: dict, session_id: str) -> JSONResponse:
    """
    Complete the current order and save it to the database

    Args:
        parameters: Parameters from Dialogflow
        session_id: Session ID from Dialogflow

    Returns:
        JSONResponse: Response to send back to Dialogflow
    """
    logger.info(f"Completing order for session {session_id}")

    if session_id not in inprogress_orders:
        logger.warning(f"No in-progress order found for session {session_id}")
        fulfillment_text = "I'm having a trouble finding your order. Sorry! Can you place a new order please?"
    else:
        try:
            order = inprogress_orders[session_id]
            logger.info(f"Found in-progress order for session {session_id}: {order}")

            order_id = save_to_db(order)
            if order_id == -1:
                logger.error(f"Failed to save order to database for session {session_id}")
                fulfillment_text = "Sorry, I couldn't process your order due to a backend error. " \
                                "Please place a new order again"
            else:
                order_total = db_helper.get_total_order_price(order_id)
                logger.info(f"Order {order_id} completed successfully with total: {order_total}")

                fulfillment_text = f"Awesome. We have placed your order. " \
                            f"Here is your order id # {order_id}. " \
                            f"Your order total is ${order_total:.2f} which you can pay at the time of delivery!"

            # Remove the order from in-progress orders
            del inprogress_orders[session_id]
            logger.info(f"Removed in-progress order for session {session_id}")

        except Exception as e:
            logger.error(f"Error completing order: {str(e)}", exc_info=True)
            fulfillment_text = "Sorry, something went wrong while processing your order. Please try again."

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })


def add_to_order(parameters: dict, session_id: str) -> JSONResponse:
    """
    Add items to the current order

    Args:
        parameters: Parameters from Dialogflow
        session_id: Session ID from Dialogflow

    Returns:
        JSONResponse: Response to send back to Dialogflow
    """
    try:
        logger.info(f"Adding items to order for session {session_id}")

        # Extract food items and quantities from parameters
        food_items = parameters.get("food-item", [])
        quantities = parameters.get("number", [])

        logger.info(f"Food items: {food_items}, Quantities: {quantities}")

        # Validate input parameters
        if not food_items:
            logger.warning("No food items specified")
            fulfillment_text = "Please specify which food items you'd like to order."
        elif not quantities:
            logger.warning("No quantities specified")
            fulfillment_text = "Please specify the quantities for your food items."
        elif len(food_items) != len(quantities):
            logger.warning(f"Mismatch between food items and quantities: {len(food_items)} items, {len(quantities)} quantities")
            fulfillment_text = "Sorry, the number of food items and quantities don't match. Please specify both items and their quantities clearly."
        else:
            # Validate quantities are positive numbers
            try:
                validated_quantities = []
                for qty in quantities:
                    if isinstance(qty, (int, float)) and qty > 0:
                        validated_quantities.append(int(qty))
                    else:
                        raise ValueError(f"Invalid quantity: {qty}")

                # Create a dictionary of food items and quantities
                new_food_dict = dict(zip(food_items, validated_quantities))

                # Update the in-progress order
                if session_id in inprogress_orders:
                    logger.info(f"Updating existing order for session {session_id}")
                    current_food_dict = inprogress_orders[session_id]
                    # Update quantities (add to existing or create new)
                    for item, qty in new_food_dict.items():
                        current_food_dict[item] = current_food_dict.get(item, 0) + qty
                    inprogress_orders[session_id] = current_food_dict
                else:
                    logger.info(f"Creating new order for session {session_id}")
                    inprogress_orders[session_id] = new_food_dict

                # Generate a string representation of the order
                order_str = generic_helper.get_str_from_food_dict(inprogress_orders[session_id])
                fulfillment_text = f"Great! I've added that to your order. So far you have: {order_str}. Would you like to add anything else?"

            except ValueError as ve:
                logger.error(f"Invalid quantity value: {ve}")
                fulfillment_text = "Please provide valid quantities (positive numbers) for your food items."

    except Exception as e:
        logger.error(f"Error adding to order: {str(e)}", exc_info=True)
        fulfillment_text = "Sorry, something went wrong while adding items to your order. Please try again."

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })


def remove_from_order(parameters: dict, session_id: str) -> JSONResponse:
    """
    Remove items from the current order

    Args:
        parameters: Parameters from Dialogflow
        session_id: Session ID from Dialogflow

    Returns:
        JSONResponse: Response to send back to Dialogflow
    """
    try:
        logger.info(f"Removing items from order for session {session_id}")

        if session_id not in inprogress_orders:
            logger.warning(f"No in-progress order found for session {session_id}")
            return JSONResponse(content={
                "fulfillmentText": "I'm having a trouble finding your order. Sorry! Can you place a new order please?"
            })

        # Extract food items from parameters
        food_items = parameters.get("food-item", [])
        logger.info(f"Food items to remove: {food_items}")

        current_order = inprogress_orders[session_id]
        logger.info(f"Current order: {current_order}")

        removed_items = []
        no_such_items = []

        # Remove items from the order
        for item in food_items:
            if item not in current_order:
                no_such_items.append(item)
            else:
                removed_items.append(item)
                del current_order[item]

        # Generate response based on what was removed
        if len(removed_items) > 0:
            fulfillment_text = f'Removed {", ".join(removed_items)} from your order!'
        else:
            fulfillment_text = ""

        if len(no_such_items) > 0:
            fulfillment_text += f' Your current order does not have {", ".join(no_such_items)}.'

        if len(current_order.keys()) == 0:
            fulfillment_text += " Your order is empty!"
        else:
            order_str = generic_helper.get_str_from_food_dict(current_order)
            fulfillment_text += f" Here is what is left in your order: {order_str}"

        logger.info(f"Updated order: {current_order}")

    except Exception as e:
        logger.error(f"Error removing from order: {str(e)}", exc_info=True)
        fulfillment_text = "Sorry, something went wrong while removing items from your order. Please try again."

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })


def track_order(parameters: dict, session_id: str) -> JSONResponse:
    """
    Track the status of an order

    Args:
        parameters: Parameters from Dialogflow
        session_id: Session ID from Dialogflow

    Returns:
        JSONResponse: Response to send back to Dialogflow
    """
    try:
        # Extract order ID from parameters
        order_id = int(parameters.get('order_id', 0))
        logger.info(f"Tracking order {order_id}")

        if order_id <= 0:
            logger.warning(f"Invalid order ID: {order_id}")
            return JSONResponse(content={
                "fulfillmentText": "Please provide a valid order ID to track your order."
            })

        # Get the order status from the database
        order_status = db_helper.get_order_status(order_id)

        if order_status:
            logger.info(f"Order {order_id} status: {order_status}")
            fulfillment_text = f"The order status for order id: {order_id} is: {order_status}"
        else:
            logger.warning(f"No order found with ID: {order_id}")
            fulfillment_text = f"No order found with order id: {order_id}"

    except ValueError:
        logger.error(f"Invalid order ID format: {parameters.get('order_id', '')}")
        fulfillment_text = "Please provide a valid order ID number."

    except Exception as e:
        logger.error(f"Error tracking order: {str(e)}", exc_info=True)
        fulfillment_text = "Sorry, something went wrong while tracking your order. Please try again."

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })