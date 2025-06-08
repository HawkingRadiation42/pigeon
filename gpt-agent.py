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
    
    # Start interactive chat
    print("🎯 Starting interactive chat mode...")
    agent.initiate_chat_agent() 