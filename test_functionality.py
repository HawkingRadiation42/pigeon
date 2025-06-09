#!/usr/bin/env python3
"""
Test script to demonstrate the exact functionality:
1. Check if queue is empty
2. If empty, add new message (from, to, body) to MongoDB
3. Get all data from MongoDB as JSON
4. Call send_gpt function
"""

from message_processor import process_message_if_queue_empty
from rabbitmq_service import rabbitmq_service

def test_functionality():
    print("=== Testing Core Functionality ===\n")
    
    # Test message data
    from_number = "+1234567890"
    to_number = "+0987654321"
    body = "Hello, this is a test message!"
    message_sid = "SM123456"
    account_sid = "AC789012"
    
    print(f"Test message:")
    print(f"From: {from_number}")
    print(f"To: {to_number}")
    print(f"Body: {body}")
    print()
    
    # Check current queue status
    print("1. Checking queue status...")
    is_empty = rabbitmq_service.is_queue_empty("sms_messages")
    print(f"Queue is empty: {is_empty}")
    print()
    
    # Call the main function
    print("2. Calling process_message_if_queue_empty...")
    result = process_message_if_queue_empty(
        from_number=from_number,
        to_number=to_number,
        body=body,
        message_sid=message_sid,
        account_sid=account_sid
    )
    
    print(f"Result status: {result['status']}")
    print(f"Message: {result.get('message', 'No message')}")
    
    if result['status'] == 'success':
        print(f"Total messages in DB: {result.get('total_messages_in_db', 0)}")
        
        gpt_response = result.get('gpt_response', {})
        if gpt_response.get('status') == 'success':
            analysis = gpt_response.get('analysis', {})
            print(f"\nGPT Analysis:")
            print(f"- Total messages: {analysis.get('total_messages', 0)}")
            print(f"- Unique senders: {analysis.get('unique_senders', 0)}")
            print(f"- Total characters: {analysis.get('total_characters', 0)}")
            print(f"- Average message length: {analysis.get('average_message_length', 0):.1f}")
            print(f"- Summary: {gpt_response.get('summary', 'No summary')}")
    
    print(f"\n3. Final queue status...")
    is_empty_after = rabbitmq_service.is_queue_empty("sms_messages")
    print(f"Queue is empty after processing: {is_empty_after}")

if __name__ == "__main__":
    test_functionality() 