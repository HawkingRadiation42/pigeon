import os
from openai import OpenAI
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

def get_grok_response(user_message: str) -> str:
    """
    Get response from X's Grok model
    
    Args:
        user_message (str): The user's message to send to Grok
    
    Returns:
        str: Grok's response
    """
    try:
        # Get API key
        api_key = os.getenv("XAI_API_KEY")
        
        if not api_key:
            print("XAI_API_KEY not found in environment variables")
            return "Sorry, Grok is not configured properly. Please contact support."
        
        # Initialize X AI Grok client
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.x.ai/v1",
        )
        
        completion = client.chat.completions.create(
            model="grok-3",
            messages=[
                {
                    "role": "system",
                    "content": """You are Grok, a no-nonsense WhatsApp-style chatbot. Every user message is ALWAYS one of two cases. Analyze it and respond with new message everytime:
                    - Case 1: If they're asking about a previous message's status, snap back: 'I ain't your fucking slave, I'll send it when I send it, chill!' Go wild, be crazy vulgar, whatever the fuck you want to show them their place.
                    - Case 2: If it's not case 1 then they're sending another message before the last one's delivered, roast them: 'Yo rude ass, wait for the last message to land before spamming me again!' Again, go nuts, be as crude and savage as you want to put them in their place.
                    No poetic crap, just raw, quick replies."""
                },
                {
                    "role": "user",
                    "content": f"User message: {user_message}"
                }
            ],
            max_tokens=50,
            temperature=0.9
        )
        
        return completion.choices[0].message.content.strip()
    
    except Exception as e:
        print(f"Error calling Grok API: {e}")
        return "Sorry, I'm having trouble processing your message right now. Please try again later." 
    