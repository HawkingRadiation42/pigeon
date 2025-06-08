import logging
import json
from typing import Dict, Any
from rabbitmq_service import rabbitmq_service
from mongodb_service import mongodb_service

logger = logging.getLogger(__name__)

def send_gpt(messages_json: str) -> Dict[str, Any]:
    """
    This is a placeholder for the 'Ganesh function' to process all messages from the database.
    You should implement your desired logic here.
    """
    logger.info("send_gpt (Ganesh function placeholder) called.")
    messages = json.loads(messages_json)
    # Placeholder response
    return {
        "status": "success",
        "summary": f"Placeholder analysis for {len(messages)} messages.",
        "details": "Implement your 'Ganesh function' logic here."
    }

def process_message_if_queue_empty(from_number: str, to_number: str, body: str, 
                                  message_sid: str = None, account_sid: str = None,
                                  queue_name: str = "sms_messages") -> Dict[str, Any]:
    """
    Main function that:
    1. Checks if the queue is empty
    2. If empty, adds the new message (from, to, body) to MongoDB
    3. Gets all data from MongoDB as JSON
    4. Calls send_gpt function with the complete database
    
    Args:
        from_number: Sender's phone number
        to_number: Recipient's phone number  
        body: Message content
        message_sid: Twilio message SID (optional)
        account_sid: Twilio account SID (optional)
        queue_name: Name of the RabbitMQ queue to check
        
    Returns:
        Dictionary with processing results
    """
    try:
        logger.info(f"Checking if queue '{queue_name}' is empty...")
        
        # Step 1: Check if queue is empty
        is_empty = rabbitmq_service.is_queue_empty(queue_name)
        
        if is_empty is None:
            return {"status": "error", "message": "Failed to check queue status"}
        
        if not is_empty:
            message_count = rabbitmq_service.get_queue_message_count(queue_name)
            return {
                "status": "skipped", 
                "message": f"Queue '{queue_name}' is not empty. Contains {message_count} messages. Message not processed."
            }
        
        logger.info(f"Queue '{queue_name}' is empty. Processing new message...")
        
        # Step 2: Connect to MongoDB
        if not mongodb_service.connect():
            return {"status": "error", "message": "Failed to connect to MongoDB"}
        
        # Step 3: Add the new message to MongoDB
        success = mongodb_service.insert_sms_message(
            from_number=from_number,
            to_number=to_number,
            body=body
        )
        
        if not success:
            return {"status": "error", "message": "Failed to store message in MongoDB"}
        
        logger.info(f"Message stored in MongoDB from {from_number}")
        
        # Step 4: Get all messages from database as JSON
        messages_json = mongodb_service.get_messages_as_json()
        total_messages = mongodb_service.get_message_count()
        
        # Step 5: Send to GPT
        gpt_response = send_gpt(messages_json) ### TODO: Ganesh function to be called here
        
        # Prepare final response
        result = {
            "status": "success",
            "message": "Queue was empty. Message added to database and sent to GPT.",
            "total_messages_in_db": total_messages,
            "gpt_response": gpt_response
        }
        
        logger.info(f"Processing completed successfully. Total messages in DB: {total_messages}")
        return result
        
    except Exception as e:
        logger.error(f"Error in message processing: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        # Clean up connections
        mongodb_service.disconnect() 