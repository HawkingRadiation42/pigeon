# Pigeon FastAPI Project

A simple FastAPI project with Twilio SMS webhook support.

## Features

- **POST /message**: Twilio SMS webhook handler - receives SMS messages and returns "hello world" (TwiML)
- **GET /health**: Health check endpoint

## Setup Instructions

### Prerequisites

Make sure you have `uv` installed. If not, install it:

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or using pip
pip install uv
```

### Installation

1. **Clone/Navigate to the project directory**:
   ```bash
   cd pigeon
   ```

2. **Create a virtual environment and install dependencies**:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -r requirements.txt
   ```

   Alternatively, you can install dependencies directly:
   ```bash
   uv pip install fastapi uvicorn[standard] pydantic python-multipart
   ```

### Running the Server

Start the FastAPI server using uvicorn:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The server will start and be available at:
- **API Base URL**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## Twilio Integration

### Setting up Twilio SMS Webhook

1. **Get your server URL**: 
   - For local development, use ngrok: `ngrok http 8000`
   - For production, use your domain: `https://yourdomain.com`

2. **Configure Twilio Console**:
   - Go to [Twilio Console](https://console.twilio.com/)
   - Navigate to Phone Numbers → Manage → Active numbers
   - Click on your Twilio phone number
   - Set the SMS webhook URL: `https://your-domain.com/message`

3. **Test with ngrok (for local development)**:
   ```bash
   # In one terminal
   uvicorn main:app --reload
   
   # In another terminal
   ngrok http 8000
   ```
   Use the ngrok HTTPS URL for your webhook configuration: `https://abc123.ngrok.io/message`

### How it works

When someone sends an SMS to your Twilio number:
1. Twilio receives the SMS
2. Twilio sends a POST request to your `/message` endpoint with form data:
   ```
   From=+1234567890
   To=+0987654321
   Body=Hello there!
   MessageSid=SM123abc456def
   AccountSid=AC123...
   ```
3. Your API responds with TwiML to send "hello world" back:
   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <Response>
       <Message>hello world</Message>
   </Response>
   ```
4. Twilio sends the "hello world" message back to the original sender

## Testing the API Endpoints

### Health Check Endpoint

```bash
curl -X GET "http://localhost:8000/health"
```

Expected response:
```json
{"status": "ok"}
```

### Message Endpoint (Simulate Twilio webhook)

```bash
curl -X POST "http://localhost:8000/message" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "From=%2B1234567890&To=%2B0987654321&Body=Test%20message&MessageSid=SM123abc456def"
```

Expected response (TwiML):
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>hello world</Message>
</Response>
```

### Using the Interactive Documentation

1. Open your browser and go to http://localhost:8000/docs
2. You'll see the Swagger UI with both endpoints
3. Click on any endpoint to expand it
4. Click "Try it out" to test the endpoints

## API Endpoints

| Method | Endpoint | Description | Request Format | Response Format |
|--------|----------|-------------|----------------|-----------------|
| GET | `/health` | Health check | None | JSON |
| POST | `/message` | Twilio SMS webhook | Form data | TwiML (XML) |

## Development

To run in development mode with auto-reload:

```bash
uvicorn main:app --reload
```

This will automatically restart the server when you make changes to the code.

## Production Notes

- Use HTTPS in production for Twilio webhooks
- The `/message` endpoint logs incoming messages to console - customize this for your needs
- Consider implementing Twilio request validation for security in production
