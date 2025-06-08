import os
import asyncio
from fastapi import FastAPI, Form, BackgroundTasks
from fastapi.responses import Response
from pydantic import BaseModel
from twilio.rest import Client
from dotenv import load_dotenv
from utils.grok_client import get_grok_response

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="Pigeon API", description="A simple FastAPI project with Twilio SMS webhook support", version="1.0.0")

# Twilio client setup
client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)

class HealthResponse(BaseModel):
    status: str

async def send_delayed_message(to_number: str, from_number: str, original_message: str):
    """Send a delayed message after 10 seconds with Grok's response"""
    await asyncio.sleep(1)  # Wait 10 seconds
    
    try:
        # Get Grok's response to the user message
        grok_response = get_grok_response(original_message)
        
        message = client.messages.create(
            body=grok_response,
            from_=from_number,  # Use the same Twilio number that received the message
            to=to_number
        )
        print(f"Delayed Grok message sent successfully. SID: {message.sid}")
        print(f"Grok response: {grok_response}")
    except Exception as e:
        print(f"Error sending delayed message: {e}")

@app.post("/message", response_class=Response)
async def handle_message(
    background_tasks: BackgroundTasks,
    From: str = Form(...),
    To: str = Form(...),
    Body: str = Form(...),
    MessageSid: str = Form(...),
    AccountSid: str = Form(None)
):
    """
    Handle incoming SMS messages from Twilio.
    Schedules a delayed Grok AI response back to sender after 10 seconds.
    Returns TwiML response.
    """
    # Log the incoming message
    print(f"Received SMS from {From} to {To}: {Body}")
    
    # Schedule delayed Grok response to be sent back to the sender
    background_tasks.add_task(send_delayed_message, From, To, Body)
    
    # Return immediate TwiML response
    twiml_response = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>Message received! Grok is thinking... You'll get an AI response in 10 seconds.</Message>
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