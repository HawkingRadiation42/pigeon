from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
from rabbitmq_service import rabbitmq_service
from mongodb_service import mongodb_service
from message_processor import process_message_if_queue_empty
from twilio.rest import Client
import os
from dotenv import load_dotenv
from grok_client import get_grok_response

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Pigeon API", description="A FastAPI project with Twilio SMS webhook support, RabbitMQ integration, and MongoDB storage", version="1.0.0")

# Queue name for SMS messages
SMS_QUEUE_NAME = "pigeon_queue"

client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)

class HealthResponse(BaseModel):
    status: str


@app.on_event("startup")
async def startup_event():
    """Initialize RabbitMQ and MongoDB connections on startup."""
    logger.info("Starting up Pigeon API...")
    
    # Initialize RabbitMQ
    if rabbitmq_service.connect():
        rabbitmq_service.declare_queue(SMS_QUEUE_NAME)
        logger.info("RabbitMQ connection established and SMS queue declared")
    else:
        logger.warning("Failed to connect to RabbitMQ on startup")
    
    # Initialize MongoDB
    if mongodb_service.connect():
        logger.info("MongoDB connection established")
    else:
        logger.warning("Failed to connect to MongoDB on startup")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up connections on shutdown."""
    logger.info("Shutting down Pigeon API...")
    rabbitmq_service.disconnect()
    mongodb_service.disconnect()

@app.post("/message", response_class=Response)
async def handle_message(
    From: str = Form(...),
    To: str = Form(...),
    Body: str = Form(...),
    MessageSid: str = Form(...),
    AccountSid: str = Form(None)
):
    """
    Handle incoming SMS messages from Twilio.
    Checks if queue is empty, if so processes the message directly.
    Otherwise, publishes to queue.
    """
    # Log the incoming message
    logger.info(f"Received SMS from {From} to {To}: {Body}")
    
    try:
        # Check if queue is empty and process accordingly
        result = process_message_if_queue_empty(
            from_number=From,
            to_number=To,
            body=Body,
            message_sid=MessageSid,
            account_sid=AccountSid,
            queue_name=SMS_QUEUE_NAME
        )
        
        if result["status"] == "success":
            # queue is empty, so processing the message. 
            logger.info(f"Message processed successfully: {MessageSid}")
            response_message = "Message processed and analyzed"
        elif result["status"] == "success":
            # Queue is not empty, so call Grok and send response directly via Twilio API
            try:
                grok_response = get_grok_response(Body)
                message = client.messages.create(
                    body=grok_response,
                    from_=To,  # Your Twilio number (the one that received the message)
                    to=From   # Send back to the original sender
                )
                logger.info(f"Grok response sent via Twilio API: {message.sid}")
                
                # Return empty TwiML response since we already sent the message
                return Response(content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>', 
                              media_type="application/xml")
                
            except Exception as e:
                logger.error(f"Error sending Grok response: {e}")
                response_message = "Message received"
        else:
            logger.error(f"Error processing message: {result.get('message')}")
            response_message = "Message received but processing failed"
            
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        response_message = "Message received"
    
    # Return TwiML response (only for success case or errors)
    twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{response_message}</Message>
</Response>"""
    
    return Response(content=twiml_response, media_type="application/xml")

@app.get("/health", response_model=HealthResponse)
async def get_health():
    """
    Health check endpoint.
    """
    return HealthResponse(status="ok")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 