import os
from dotenv import load_dotenv
from openai import OpenAI  # pip install python-dotenv openai

load_dotenv()
# api_key = os.getenv("XAI_API_KEY")  # or set directly
api_key = "xai-lxqCu6skpHuDgvmBxp0PRDyfqp749YFVR7t8YVAVtoaJtlDYJMPKwpgFo8ZTrNjX4QC2e8F1nhGca8Th"

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