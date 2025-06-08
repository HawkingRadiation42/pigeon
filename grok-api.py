import os
from dotenv import load_dotenv
from openai import OpenAI  # pip install python-dotenv openai

load_dotenv()

# Load API keys from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")

# Use the GROQ API key for Grok API (assuming it's the same as XAI)
api_key = groq_api_key

# Initialize the OpenAI client with your API key and base URL
client = OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")

# Make a chat completion request
completion = client.chat.completions.create(
    model="grok-3-mini-beta",  # or grok-3-mini-beta, etc.
    messages=[
        {"role": "user", "content": "What is the meaning of life?"}
    ]
)

# Print the response
print(completion.choices[0].message.content)