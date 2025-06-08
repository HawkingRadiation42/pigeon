import pika
import json
import logging
from typing import Optional, Dict, Any
from pika.exceptions import AMQPConnectionError, AMQPChannelError

logger = logging.getLogger(__name__)

class RabbitMQService:
    def __init__(self, host: str = "localhost", port: int = 5672, username: str = "guest", password: str = "guest"):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.connection = None
        self.channel = None
        
    def connect(self) -> bool:
        """
        Establish connection to RabbitMQ server.
        Returns True if successful, False otherwise.
        """
        try:
            credentials = pika.PlainCredentials(self.username, self.password)
            parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                credentials=credentials
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            logger.info(f"Connected to RabbitMQ at {self.host}:{self.port}")
            return True
        except AMQPConnectionError as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            return False
    
    def disconnect(self):
        """Close the connection to RabbitMQ."""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("Disconnected from RabbitMQ")
    
    def declare_queue(self, queue_name: str, durable: bool = True) -> bool:
        """
        Declare a queue.
        Returns True if successful, False otherwise.
        """
        try:
            if not self.channel:
                if not self.connect():
                    return False
            
            self.channel.queue_declare(queue=queue_name, durable=durable)
            logger.info(f"Queue '{queue_name}' declared successfully")
            return True
        except AMQPChannelError as e:
            logger.error(f"Failed to declare queue '{queue_name}': {e}")
            return False
    
    def publish_message(self, queue_name: str, message: Dict[Any, Any], durable: bool = True) -> bool:
        """
        Publish a message to the specified queue.
        Returns True if successful, False otherwise.
        """
        try:
            if not self.channel:
                if not self.connect():
                    return False
            
            # Declare queue if it doesn't exist
            self.declare_queue(queue_name, durable)
            
            # Publish message
            self.channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2 if durable else 1  # Make message persistent if durable
                )
            )
            logger.info(f"Message published to queue '{queue_name}': {message}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish message to queue '{queue_name}': {e}")
            return False
    
    def consume_message(self, queue_name: str) -> Optional[Dict[Any, Any]]:
        """
        Consume a single message from the specified queue.
        Returns the message as a dictionary if available, None otherwise.
        """
        try:
            if not self.channel:
                if not self.connect():
                    return None
            
            # Declare queue if it doesn't exist
            self.declare_queue(queue_name)
            
            # Get a single message
            method_frame, header_frame, body = self.channel.basic_get(queue=queue_name, auto_ack=True)
            
            if method_frame:
                message = json.loads(body.decode('utf-8'))
                logger.info(f"Message consumed from queue '{queue_name}': {message}")
                return message
            else:
                logger.info(f"No messages available in queue '{queue_name}'")
                return None
                
        except Exception as e:
            logger.error(f"Failed to consume message from queue '{queue_name}': {e}")
            return None
    
    def is_queue_empty(self, queue_name: str) -> Optional[bool]:
        """
        Check if the specified queue is empty.
        Returns True if empty, False if not empty, None if error occurred.
        """
        try:
            if not self.channel:
                if not self.connect():
                    return None
            
            # Declare queue if it doesn't exist
            self.declare_queue(queue_name)
            
            # Get queue information
            method = self.channel.queue_declare(queue=queue_name, passive=True)
            message_count = method.method.message_count
            
            is_empty = message_count == 0
            logger.info(f"Queue '{queue_name}' has {message_count} messages. Empty: {is_empty}")
            return is_empty
            
        except Exception as e:
            logger.error(f"Failed to check if queue '{queue_name}' is empty: {e}")
            return None
    
    def get_queue_message_count(self, queue_name: str) -> Optional[int]:
        """
        Get the number of messages in the specified queue.
        Returns message count if successful, None if error occurred.
        """
        try:
            if not self.channel:
                if not self.connect():
                    return None
            
            # Declare queue if it doesn't exist
            self.declare_queue(queue_name)
            
            # Get queue information
            method = self.channel.queue_declare(queue=queue_name, passive=True)
            message_count = method.method.message_count
            
            logger.info(f"Queue '{queue_name}' has {message_count} messages")
            return message_count
            
        except Exception as e:
            logger.error(f"Failed to get message count for queue '{queue_name}': {e}")
            return None
    
    def purge_queue(self, queue_name: str) -> bool:
        """
        Remove all messages from the specified queue.
        Returns True if successful, False otherwise.
        """
        try:
            if not self.channel:
                if not self.connect():
                    return False
            
            # Declare queue if it doesn't exist
            self.declare_queue(queue_name)
            
            # Purge the queue
            self.channel.queue_purge(queue=queue_name)
            logger.info(f"Queue '{queue_name}' purged successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to purge queue '{queue_name}': {e}")
            return False

# Global instance
rabbitmq_service = RabbitMQService() 