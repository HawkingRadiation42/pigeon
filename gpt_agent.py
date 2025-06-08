import os
from dotenv import load_dotenv
from openai import OpenAI
from typing import List, Dict, Optional

# Load environment variables from .env file
load_dotenv()


class ChatAgent:
    """
    A class-based GPT-4 Chat Agent with conversation management capabilities
    """
    
    def __init__(self, model="gpt-4", system_message=None):
        """
        Initialize the ChatAgent with OpenAI client and default settings
        
        Args:
            model (str): The GPT model to use (default: "gpt-4")
            system_message (str): Custom system message for the AI personality
        """
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model
        self.conversation_history = []
        
        # Set default system message if none provided
        default_system_message = "You are a helpful, friendly, and knowledgeable AI assistant. Respond in a conversational and engaging manner."
        self.system_message = system_message or default_system_message
        
        # Initialize conversation with system message
        self.reset_conversation()
    
    def reset_conversation(self):
        """Reset the conversation history with the system message"""
        self.conversation_history = [
            {"role": "system", "content": self.system_message}
        ]
    
    def add_message(self, role: str, content: str):
        """
        Add a message to the conversation history
        
        Args:
            role (str): The role of the message sender ("user", "assistant", "system")
            content (str): The content of the message
        """
        self.conversation_history.append({"role": role, "content": content})
    
    def get_response(self, user_message: str, max_tokens=500, temperature=0.7) -> Optional[str]:
        """
        Get a response from GPT-4 for a single user message
        
        Args:
            user_message (str): The user's message
            max_tokens (int): Maximum tokens in the response
            temperature (float): Creativity level (0.0 to 1.0)
            
        Returns:
            str: The AI's response or None if error occurred
        """
        try:
            # Add user message to conversation
            self.add_message("user", user_message)
            
            # Make API call to GPT-4
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.conversation_history,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            # Extract and store the bot's response
            bot_response = response.choices[0].message.content
            self.add_message("assistant", bot_response)
            
            return bot_response
            
        except Exception as e:
            print(f"❌ Error getting response: {e}")
            return None
    
    def process_conversation_list(self, conversations: List[str]) -> List[Dict[str, str]]:
        """
        Process a list of conversation strings and get responses for each
        
        Args:
            conversations (List[str]): List of user messages/questions
            
        Returns:
            List[Dict[str, str]]: List of conversation pairs with user messages and AI responses
        """
        results = []
        
        print(f"🔄 Processing {len(conversations)} conversations...")
        print("=" * 60)
        
        for i, user_message in enumerate(conversations, 1):
            print(f"\n📝 Conversation {i}/{len(conversations)}")
            print(f"👤 User: {user_message}")
            
            # Get response from GPT-4
            bot_response = self.get_response(user_message)
            
            if bot_response:
                print(f"🤖 Bot: {bot_response}")
                results.append({
                    "user_message": user_message,
                    "bot_response": bot_response,
                    "conversation_number": i
                })
            else:
                print("❌ Failed to get response")
                results.append({
                    "user_message": user_message,
                    "bot_response": "Error: Could not get response",
                    "conversation_number": i
                })
            
            print("-" * 60)
        
        return results
    
    def initiate_chat_agent(self):
        """
        Start an interactive chat session with the GPT-4 agent
        """
        print("🤖 ChatGPT-4 Agent Started!")
        print(f"🧠 Model: {self.model}")
        print("💬 Start chatting (type 'quit', 'exit', or 'bye' to stop)")
        print("🔄 Type 'reset' to clear conversation history")
        print("-" * 60)
        
        while True:
            # Get user input
            user_input = input("\n👤 You: ").strip()
            
            # Check for exit commands
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\n🤖 Bot: Goodbye! Have a great day! 👋")
                break
            
            # Check for reset command
            if user_input.lower() == 'reset':
                self.reset_conversation()
                print("\n🔄 Conversation history cleared!")
                continue
            
            # Skip empty inputs
            if not user_input:
                continue
            
            # Get and display response
            bot_response = self.get_response(user_input)
            if bot_response:
                print(f"\n🤖 Bot: {bot_response}")
            else:
                print("\n❌ Sorry, I couldn't process your message. Please try again.")
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """
        Get the current conversation history
        
        Returns:
            List[Dict[str, str]]: The conversation history
        """
        return self.conversation_history.copy()
    
    def quick_question(self, question: str) -> Optional[str]:
        """
        Ask a quick question without affecting the main conversation history
        
        Args:
            question (str): The question to ask
            
        Returns:
            str: The AI's response or None if error occurred
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_message},
                    {"role": "user", "content": question}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            return f"Error: {e}"
    
    def analyze_time_sensitive_conversation(self, conversation_array: List[Dict]) -> Dict[str, str]:
        """
        Analyze a multi-turn conversation for time-sensitive content and determine delay
        
        Args:
            conversation_array (List[Dict]): Array of conversation dictionaries
            
        Returns:
            Dict[str, str]: Dictionary with delay information {"delay": "..."}
        """
        import json
        
        try:
            # Stringify the JSON array
            conversation_json = json.dumps(conversation_array, indent=2)
            
            # Create the prompt with the conversation data
            prompt = f"""Expected LLM Behaviour:
Go through multi-turn conversation and determine if its time-sensitive and respond back with worst time possible. if it's timesensitive give back worst time.

LLM should comeup with just time the worst time that LLM responds to cancel the plan.

Output should be `{{"delay": ""}}`.

If its greeting or casual message until you see plan, just respond back appropriately. If you see plan respond with worst time in the json otherwise delay should be 0.

If its plan to start something, just return 0. once the plan is ON then delay the response when terms like ETA or timesensitive messages comes.

for instance, 
If its movie plan, return delay 2 hours
If its dinner plan, return delay 1 hour
If its lunch plan, return delay 30 mins
If its breakfast plan, return delay 15 mins
If its brunch plan, return delay 1 hour
If its lunch plan, return delay 30 mins
If its breakfast plan, return delay 15 mins
If its brunch plan, return delay 1 hour
If its death message, return delay 1 month

For the below multi-turn conversation:

\"\"\"
{conversation_json}
\"\"\"
"""
            
            # Make API call to analyze the conversation
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing conversations for time-sensitive content. Always respond with valid JSON format."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.3  # Lower temperature for more consistent JSON output
            )
            
            # Get the response content
            response_content = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            try:
                # Try to find JSON in the response
                import re
                json_match = re.search(r'\{.*?"delay".*?\}', response_content, re.DOTALL)
                
                if json_match:
                    json_str = json_match.group()
                    delay_data = json.loads(json_str)
                    return delay_data
                else:
                    # If no JSON found, try to parse the entire response
                    delay_data = json.loads(response_content)
                    return delay_data
                    
            except json.JSONDecodeError:
                # If JSON parsing fails, extract delay value manually
                delay_value = "0"
                if "delay" in response_content.lower():
                    # Try to extract delay value from text
                    delay_match = re.search(r'"delay":\s*"([^"]*)"', response_content)
                    if delay_match:
                        delay_value = delay_match.group(1)
                
                return {"delay": delay_value}
                
        except Exception as e:
            print(f"❌ Error analyzing conversation: {e}")
            return {"delay": "0"}
    
    def test_time_sensitive_analysis(self):
        """
        Test function to demonstrate time-sensitive conversation analysis
        """
        import json
        
        # Example conversation arrays for testing
        test_conversations = [
            # Test 1: Casual greeting
            [
                {"role": "user", "content": "Hello there!"},
                {"role": "assistant", "content": "Hi! How can I help you today?"},
                {"role": "user", "content": "Just saying hi, have a great day!"}
            ],
            
            # Test 2: Planning something
            [
                {"role": "user", "content": "Hey, want to meet for lunch?"},
                {"role": "assistant", "content": "Sure! What time works for you?"},
                {"role": "user", "content": "How about 12:30 PM at the cafe?"},
                {"role": "assistant", "content": "Perfect, see you at 12:30!"},
                {"role": "user", "content": "What's your ETA? I'm already here"}
            ],
            
            # Test 3: Time-sensitive request
            [
                {"role": "user", "content": "Emergency! Can you help me right now?"},
                {"role": "assistant", "content": "Of course! What do you need?"},
                {"role": "user", "content": "I need this done in 10 minutes, it's urgent!"}
            ]
        ]
        
        print("🧪 Testing Time-Sensitive Conversation Analysis")
        print("=" * 60)
        
        for i, conversation in enumerate(test_conversations, 1):
            print(f"\n📝 Test Case {i}:")
            print("Conversation:", json.dumps(conversation, indent=2))
            
            result = self.analyze_time_sensitive_conversation(conversation)
            print(f"🎯 Analysis Result: {result}")
            print("-" * 40)

if __name__ == "__main__":
    # Create a ChatAgent instance
    agent = ChatAgent()
    
    print("🚀 GPT-4 Chat Agent Demo")
    print("=" * 60)
    
    # Quick demonstration: Ask "How are you?" automatically
    print("📝 Quick question: 'How are you?'")
    response = agent.quick_question("How are you?")
    print(f"🤖 GPT-4 Response: {response}")
    
    print("\n" + "=" * 60)
    
    # Example: Process a list of conversations
    print("📋 Example: Processing conversation list...")
    example_conversations = [
        "What's the weather like?",
        "Tell me a joke",
        "What is Python programming?"
    ]
    
    # Process the conversation list
    results = agent.process_conversation_list(example_conversations)
    
    print(f"\n✅ Processed {len(results)} conversations successfully!")
    
    print("\n" + "=" * 60)
    
    # Test time-sensitive conversation analysis
    print("🧪 Testing Time-Sensitive Analysis Feature...")
    agent.test_time_sensitive_analysis()
    
    print("\n" + "=" * 60)
    
    # Start interactive chat
    print("🎯 Starting interactive chat mode...")
    agent.initiate_chat_agent() 