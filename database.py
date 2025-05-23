from pymongo import MongoClient
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
import os
from dotenv import load_dotenv
from bson import ObjectId

# Load environment variables
load_dotenv()

class Database:
    def __init__(self):
        """Initialize database connection."""
        try:
            # Get MongoDB configuration from environment variables
            host = os.getenv('MONGODB_HOST', 'localhost')
            port = int(os.getenv('MONGODB_PORT', '27017'))
            database_name = os.getenv('MONGODB_DATABASE', 'task_management')
            collection_name = os.getenv('MONGODB_COLLECTION', 'tasks')

            self.client = MongoClient(host, port)
            self.db = self.client[database_name]
            self.tasks = self.db[collection_name]
            logging.info("Successfully connected to MongoDB")
        except Exception as e:
            logging.error(f"Failed to connect to MongoDB: {str(e)}")
            raise

    def add_task(self, task_data: Dict[str, Any]) -> str:
        """Add a new task to the database."""
        try:
            task_data["creation_timestamp"] = datetime.utcnow()
            result = self.tasks.insert_one(task_data)
            return str(result.inserted_id)
        except Exception as e:
            logging.error(f"Failed to add task: {str(e)}")
            raise

    def get_tasks(self, filter_criteria: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Retrieve tasks based on filter criteria."""
        try:
            if filter_criteria is None:
                filter_criteria = {}
            return list(self.tasks.find(filter_criteria))
        except Exception as e:
            logging.error(f"Failed to retrieve tasks: {str(e)}")
            raise

    def update_task(self, task_id: str, update_data: Dict[str, Any]) -> bool:
        """Update an existing task."""
        try:
            result = self.tasks.update_one(
                {"_id": ObjectId(task_id)},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logging.error(f"Failed to update task: {str(e)}")
            raise

    def delete_task(self, task_id: str) -> bool:
        """Delete a task."""
        try:
            result = self.tasks.delete_one({"_id": ObjectId(task_id)})
            return result.deleted_count > 0
        except Exception as e:
            logging.error(f"Failed to delete task: {str(e)}")
            raise

    def mark_task_completed(self, task_id: str) -> bool:
        """Mark a task as completed."""
        try:
            result = self.tasks.update_one(
                {"_id": ObjectId(task_id)},
                {"$set": {"status": "Completed"}}
            )
            return result.modified_count > 0
        except Exception as e:
            logging.error(f"Failed to mark task as completed: {str(e)}")
            raise

    def delete_all_tasks(self) -> bool:
        """Delete all tasks from the database."""
        try:
            result = self.tasks.delete_many({})
            return result.deleted_count > 0
        except Exception as e:
            logging.error(f"Failed to delete all tasks: {str(e)}")
            raise

    def close(self):
        """Close the database connection."""
        try:
            self.client.close()
            logging.info("Database connection closed")
        except Exception as e:
            logging.error(f"Failed to close database connection: {str(e)}")
            raise 