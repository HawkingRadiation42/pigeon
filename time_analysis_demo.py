#!/usr/bin/env python3
"""
Time-Sensitive Conversation Analysis Demo

This script demonstrates how to use the ChatAgent's time-sensitive conversation analysis feature.
"""

import os
import sys
from dotenv import load_dotenv

# Import the ChatAgent class from gpt-agent.py
sys.path.append('.')
import importlib.util
spec = importlib.util.spec_from_file_location("gpt_agent", "gpt-agent.py")
gpt_agent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gpt_agent)
ChatAgent = gpt_agent.ChatAgent

# Load environment variables
load_dotenv()

def main():
    """
    Demonstrate the time-sensitive conversation analysis functionality
    """
    print("🧪 Time-Sensitive Conversation Analysis Demo")
    print("=" * 60)
    
    # Create ChatAgent instance
    agent = ChatAgent()
    
    # Example conversation datasets
    example_conversations = {
        "greeting": [
            {"role": "user", "content": "Hello there!"},
            {"role": "assistant", "content": "Hi! How can I help you today?"},
            {"role": "user", "content": "Just saying hi, have a great day!"}
        ],
        
        "casual_planning": [
            {"role": "user", "content": "Want to grab coffee sometime?"},
            {"role": "assistant", "content": "Sure! When are you free?"},
            {"role": "user", "content": "Maybe this weekend?"}
        ],
        
        "time_sensitive_plan": [
            {"role": "user", "content": "Hey, want to meet for lunch?"},
            {"role": "assistant", "content": "Sure! What time works for you?"},
            {"role": "user", "content": "How about 12:30 PM at the cafe?"},
            {"role": "assistant", "content": "Perfect, see you at 12:30!"},
            {"role": "user", "content": "What's your ETA? I'm already here"}
        ],
        
        "urgent_request": [
            {"role": "user", "content": "Emergency! Can you help me right now?"},
            {"role": "assistant", "content": "Of course! What do you need?"},
            {"role": "user", "content": "I need this done in 10 minutes, it's urgent!"}
        ],
        
        "meeting_delay": [
            {"role": "user", "content": "Are we still meeting at 3 PM?"},
            {"role": "assistant", "content": "Yes, see you at 3!"},
            {"role": "user", "content": "Running 15 minutes late, can we push it?"},
            {"role": "assistant", "content": "No worries, 3:15 works for me"},
            {"role": "user", "content": "Actually, I might need 30 minutes. Sorry!"}
        ],
        
        "movie_plan_eta": [
            {"role": "user", "content": "hi"},
            {"role": "assistant", "content": "hello, how's it going"},
            {"role": "user", "content": "it's going great, how are you"},
            {"role": "assistant", "content": "At my best, what plans for eve?"},
            {"role": "user", "content": "Let's go for movies, JohnVick"},
            {"role": "assistant", "content": "Sounds, like a plan let's do it"},
            {"role": "user", "content": "Hey, I'm at movies, movie starts in 5mins. what's your ETA?"}
        ]
    }
    
    # Analyze each conversation
    for conversation_name, conversation_data in example_conversations.items():
        print(f"\n📝 Analyzing: {conversation_name.replace('_', ' ').title()}")
        print("-" * 40)
        
        # Show the conversation
        print("Conversation:")
        for msg in conversation_data:
            role_emoji = "👤" if msg["role"] == "user" else "🤖"
            print(f"  {role_emoji} {msg['role'].title()}: {msg['content']}")
        
        # Analyze for time sensitivity
        result = agent.analyze_time_sensitive_conversation(conversation_data)
        
        # Display result
        delay = result.get('delay', '0')
        if delay == '0':
            print(f"🟢 Result: No delay needed (delay: {delay})")
        else:
            print(f"🔴 Result: Time-sensitive! Suggested delay: {delay}")
        
        print()

if __name__ == "__main__":
    main() 