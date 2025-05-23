from pymongo import MongoClient
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
import os
from dotenv import load_dotenv
from bson import ObjectId
from dateutil import parser

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

    def get_tasks(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get tasks with optional filtering."""
        try:
            if filters:
                # Handle case-insensitive title search
                if "title" in filters:
                    title = filters.pop("title")
                    filters["title"] = {"$regex": f"^{title}$", "$options": "i"}
                
                # Handle ObjectId conversion for _id
                if "_id" in filters:
                    try:
                        filters["_id"] = ObjectId(filters["_id"])
                    except Exception as e:
                        raise ValueError(f"Invalid task ID format: {str(e)}")
                
                # Handle date range filters
                if "due_date" in filters:
                    date_filter = filters["due_date"]
                    if "$gte" in date_filter and isinstance(date_filter["$gte"], str):
                        date_filter["$gte"] = parser.parse(date_filter["$gte"])
                    if "$lte" in date_filter and isinstance(date_filter["$lte"], str):
                        date_filter["$lte"] = parser.parse(date_filter["$lte"])
                    
            return list(self.tasks.find(filters))
        except Exception as e:
            logging.error(f"Failed to get tasks: {str(e)}")
            raise

    def update_task(self, task_id: ObjectId, update_data: Dict[str, Any]) -> bool:
        """Update an existing task."""
        try:
            result = self.tasks.update_one(
                {"_id": task_id},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logging.error(f"Failed to update task: {str(e)}")
            raise

    def delete_task(self, task_id: ObjectId) -> bool:
        """Delete a task."""
        try:
            result = self.tasks.delete_one({"_id": task_id})
            return result.deleted_count > 0
        except Exception as e:
            logging.error(f"Failed to delete task: {str(e)}")
            raise

    def mark_task_completed(self, task_id: ObjectId) -> bool:
        """Mark a task as completed."""
        try:
            result = self.tasks.update_one(
                {"_id": task_id},
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