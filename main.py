from fastapi import FastAPI, Form
from fastapi.responses import Response
from pydantic import BaseModel

app = FastAPI(title="Pigeon API", description="A simple FastAPI project with Twilio SMS webhook support", version="1.0.0")


class HealthResponse(BaseModel):
    status: str


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
    Returns TwiML response.
    """
    # Log the incoming message (you can add your logic here)
    print(f"Received SMS from {From} to {To}: {Body}")
    
    # Return TwiML response
    twiml_response = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>hello world</Message>
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