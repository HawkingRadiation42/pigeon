from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
import asyncio
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
    """Initialize RabbitMQ and MongoDB connections on startup and clear existing data."""
    logger.info("Starting up Pigeon API...")
    
    # Initialize RabbitMQ
    if rabbitmq_service.connect():
        rabbitmq_service.declare_queue(SMS_QUEUE_NAME)
        logger.info("RabbitMQ connection established and SMS queue declared")
        
        # Clear the queue on startup
        try:
            rabbitmq_service.purge_queue(SMS_QUEUE_NAME)
            logger.info(f"Queue '{SMS_QUEUE_NAME}' cleared on startup")
        except Exception as e:
            logger.warning(f"Failed to clear queue on startup: {e}")
    else:
        logger.warning("Failed to connect to RabbitMQ on startup")
    
    # Initialize MongoDB
    if mongodb_service.connect():
        logger.info("MongoDB connection established")
        
        # Clear the database on startup
        try:
            mongodb_service.clear_all_messages()
            logger.info("MongoDB database cleared on startup")
        except Exception as e:
            logger.warning(f"Failed to clear MongoDB on startup: {e}")
    else:
        logger.warning("Failed to connect to MongoDB on startup")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up connections on shutdown."""
    logger.info("Shutting down Pigeon API...")
    rabbitmq_service.disconnect()
    mongodb_service.disconnect()

async def send_delayed_message(to_number: str, from_number: str, original_message: str):
    """Send a delayed message after 45 seconds with Grok's response and clear the queue"""
    await asyncio.sleep(45)  # Wait 45 seconds
    
    try:
        # Get Grok's response to the user message
        grok_response = get_grok_response(original_message)
        
        # Send Grok response to original sender
        message = client.messages.create(
            body=grok_response,
            from_=from_number,  # Use the same Twilio number that received the message
            to=to_number
        )
        logger.info(f"Delayed Grok message sent successfully. SID: {message.sid}")
        logger.info(f"Grok response: {grok_response}")
        
        # Also send message to WhatsApp number
        try:
            whatsapp_message = client.messages.create(
                body=f"Delayed message from {to_number}: {original_message}\nGrok Response: {grok_response}",
                from_=from_number,  # Your Twilio number
                to="whatsapp:+917355620545"
            )
            logger.info(f"Delayed message also sent to WhatsApp number. SID: {whatsapp_message.sid}")
        except Exception as whatsapp_error:
            logger.error(f"Error sending delayed message to WhatsApp: {whatsapp_error}")
        
        # Clear the queue after sending the delayed message
        try:
            rabbitmq_service.purge_queue(SMS_QUEUE_NAME)
            logger.info(f"Queue '{SMS_QUEUE_NAME}' cleared after sending delayed message")
        except Exception as queue_error:
            logger.error(f"Error clearing queue after delayed message: {queue_error}")
            
    except Exception as e:
        logger.error(f"Error sending delayed message: {e}")

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
            # Queue is empty, so message was processed with GPT
            logger.info(f"Message processed successfully: {MessageSid}")
            
            # Get GPT response and check for delay
            try:
                gpt_response = result.get("gpt_response", {"delay": "0"})
                delay_value = gpt_response.get("delay", "0") if isinstance(gpt_response, dict) else "0"
                
                # Check if delay is greater than 0
                if delay_value != "0" and delay_value.strip():
                    logger.info(f"Delay detected: {delay_value}. Adding to queue and scheduling delayed response.")
                    
                    # Add message to queue
                    try:
                        rabbitmq_service.publish_message(SMS_QUEUE_NAME, {
                            "from": From,
                            "to": To,
                            "body": Body,
                            "message_sid": MessageSid,
                            "account_sid": AccountSid
                        })
                        logger.info(f"Message added to queue: {MessageSid}")
                    except Exception as queue_error:
                        logger.error(f"Error adding message to queue: {queue_error}")
                    
                    # Schedule delayed response (no immediate response)
                    asyncio.create_task(send_delayed_message(From, To, Body))
                    
                    # Return empty TwiML response (no message sent immediately)
                    return Response(content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>', 
                                  media_type="application/xml")
                else:
                    # No delay, send message to WhatsApp number
                    logger.info("No delay detected. Sending message to WhatsApp number.")
                    try:
                        whatsapp_message = client.messages.create(
                            body=f"{Body}",
                            from_=To,  # Your Twilio number
                            to="whatsapp:+917355620545"
                        )
                        logger.info(f"Message sent to WhatsApp number. SID: {whatsapp_message.sid}")
                    except Exception as whatsapp_error:
                        logger.error(f"Error sending message to WhatsApp: {whatsapp_error}")
                    
                    return Response(content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>', 
                                  media_type="application/xml")
                
            except Exception as e:
                logger.error(f"Error processing GPT response: {e}")
                response_message = "Message processed but failed to handle response"
            
        elif result["status"] == "skipped":
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