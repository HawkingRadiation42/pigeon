import logging
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import ConnectionFailure, PyMongoError
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class MongoDBService:
    def __init__(self, uri: str = "mongodb+srv://admin:admin@cluster0.xqctduu.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"):
        self.uri = uri
        self.client = None
        self.db = None
        self.collection = None
        
    def connect(self, database_name: str = "pigeon_db", collection_name: str = "sms_messages") -> bool:
        """
        Connect to MongoDB and set up database and collection.
        Returns True if successful, False otherwise.
        """
        try:
            self.client = MongoClient(self.uri, server_api=ServerApi('1'))
            # Test the connection
            self.client.admin.command('ping')
            
            # Set up database and collection
            self.db = self.client[database_name]
            self.collection = self.db[collection_name]
            
            logger.info(f"Connected to MongoDB database '{database_name}', collection '{collection_name}'")
            return True
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False
        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {e}")
            return False
    
    def disconnect(self):
        """Close the MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    def insert_sms_message(self, from_number: str, to_number: str, body: str, message_sid: str = None, account_sid: str = None) -> bool:
        """
        Insert an SMS message into the database.
        Returns True if successful, False otherwise.
        """
        try:
            if self.collection is None:
                if not self.connect():
                    return False
            
            # Create document
            document = {
                "from": from_number,
                "to": to_number,
                "body": body,
                "message_sid": message_sid,
                "account_sid": account_sid,
                "timestamp": datetime.utcnow(),
                "processed": True
            }
            
            # Insert document
            result = self.collection.insert_one(document)
            
            if result.inserted_id:
                logger.info(f"SMS message inserted with ID: {result.inserted_id}")
                return True
            else:
                logger.error("Failed to insert SMS message")
                return False
                
        except PyMongoError as e:
            logger.error(f"MongoDB error inserting SMS message: {e}")
            return False
        except Exception as e:
            logger.error(f"Error inserting SMS message: {e}")
            return False
    
    def get_all_messages(self) -> List[Dict[Any, Any]]:
        """
        Retrieve all SMS messages from the database.
        Returns list of messages or empty list if error.
        """
        try:
            if self.collection is None:
                if not self.connect():
                    return []
            
            # Get all messages, sorted by timestamp (newest first)
            messages = list(self.collection.find().sort("timestamp", -1))
            
            # Convert ObjectId to string for JSON serialization
            for message in messages:
                message["_id"] = str(message["_id"])
                # Convert datetime to string for JSON serialization
                if "timestamp" in message and message["timestamp"]:
                    message["timestamp"] = message["timestamp"].isoformat()
            
            logger.info(f"Retrieved {len(messages)} messages from database")
            return messages
            
        except PyMongoError as e:
            logger.error(f"MongoDB error retrieving messages: {e}")
            return []
        except Exception as e:
            logger.error(f"Error retrieving messages: {e}")
            return []
    
    def get_messages_as_json(self) -> str:
        """
        Get all messages as a JSON string.
        Returns JSON string or empty JSON array if error.
        """
        try:
            messages = self.get_all_messages()
            return json.dumps(messages, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error converting messages to JSON: {e}")
            return "[]"
    
    def clear_all_messages(self) -> bool:
        """
        Remove all messages from the database.
        Returns True if successful, False otherwise.
        """
        try:
            if self.collection is None:
                if not self.connect():
                    return False
            
            result = self.collection.delete_many({})
            logger.info(f"Deleted {result.deleted_count} messages from database")
            return True
            
        except PyMongoError as e:
            logger.error(f"MongoDB error clearing messages: {e}")
            return False
        except Exception as e:
            logger.error(f"Error clearing messages: {e}")
            return False
    
    def get_message_count(self) -> int:
        """
        Get the total number of messages in the database.
        Returns count or 0 if error.
        """
        try:
            if self.collection is None:
                if not self.connect():
                    return 0
            
            count = self.collection.count_documents({})
            logger.info(f"Total messages in database: {count}")
            return count
            
        except PyMongoError as e:
            logger.error(f"MongoDB error getting message count: {e}")
            return 0
        except Exception as e:
            logger.error(f"Error getting message count: {e}")
            return 0

# Global instance
mongodb_service = MongoDBService() 