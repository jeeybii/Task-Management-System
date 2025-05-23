from datetime import datetime
from typing import Dict, Any, Optional, List
from dateutil import parser
import logging
from bson import ObjectId

class Task:
    PRIORITY_LEVELS = ["Low", "Medium", "High"]
    STATUS_OPTIONS = ["Pending", "In Progress", "Completed"]

    def __init__(self, title: str, description: str, due_date: str,
                 priority: str, status: str = "Pending", task_id: str = None,
                 validate_past: bool = True):
        """Initialize a new task."""
        self.id = task_id
        self.title = self._validate_title(title)
        self.description = self._validate_description(description)
        self.due_date = self._parse_date(due_date, validate_past=validate_past)
        self.priority = self._validate_priority(priority)
        self.status = self._validate_status(status)
        self.creation_timestamp = datetime.utcnow()

    @staticmethod
    def _validate_title(title: str) -> str:
        """Validate task title."""
        title = title.strip()
        if not title:
            raise ValueError("Title cannot be empty")
        if len(title) > 100:  # Reasonable length limit
            raise ValueError("Title cannot be longer than 100 characters")
        return title

    @staticmethod
    def _validate_description(description: str) -> str:
        """Validate task description."""
        description = description.strip()
        if not description:
            raise ValueError("Description cannot be empty")
        if len(description) > 1000:  # Reasonable length limit
            raise ValueError("Description cannot be longer than 1000 characters")
        return description

    @staticmethod
    def _parse_date(date_str: str, validate_past: bool = True) -> datetime:
        """Parse date string to datetime object and optionally validate it's not in the past.
        
        Args:
            date_str (str): Date string in format 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM'
            validate_past (bool): Whether to validate that the date is not in the past
            
        Returns:
            datetime: Parsed datetime object
            
        Raises:
            ValueError: If date is invalid or in the past (when validate_past is True)
        """
        try:
            # Try parsing with time first
            try:
                parsed_date = parser.parse(date_str)
            except:
                # If time not provided, set to end of day (23:59:59)
                parsed_date = parser.parse(date_str)
                parsed_date = parsed_date.replace(hour=23, minute=59, second=59, microsecond=0)
            
            if validate_past:
                current_date = datetime.now()
                if parsed_date < current_date:
                    raise ValueError("Due date and time cannot be in the past")
                
            return parsed_date
        except ValueError as e:
            raise
        except Exception as e:
            raise ValueError("Invalid date format. Please use YYYY-MM-DD or YYYY-MM-DD HH:MM format.")

    @staticmethod
    def _format_datetime(dt: datetime) -> str:
        """Format datetime object for display.
        
        Args:
            dt (datetime): Datetime object to format
            
        Returns:
            str: Formatted datetime string
        """
        if dt.hour == 23 and dt.minute == 59 and dt.second == 59:
            return dt.strftime('%Y-%m-%d')
        return dt.strftime('%Y-%m-%d %H:%M')

    @staticmethod
    def _parse_filter_date(date_str: str) -> datetime:
        """Parse date string to datetime object for filtering purposes (allows past dates)."""
        return Task._parse_date(date_str, validate_past=False)

    @classmethod
    def _validate_priority(cls, priority: str) -> str:
        """Validate priority level."""
        priority = priority.strip().capitalize()  # Convert to title case
        if priority not in cls.PRIORITY_LEVELS:
            raise ValueError(f"Priority must be one of: {', '.join(cls.PRIORITY_LEVELS)}")
        return priority

    @classmethod
    def _validate_status(cls, status: str) -> str:
        """Validate status and ensure consistent formatting."""
        status = status.strip()
        
        # Convert to lowercase for comparison
        status_lower = status.lower()
        
        # Handle "In Progress" specially
        if status_lower == "in progress":
            return "In Progress"
        
        # For other statuses, convert to title case
        status = status.capitalize()
        if status not in cls.STATUS_OPTIONS:
            raise ValueError(f"Status must be one of: {', '.join(cls.STATUS_OPTIONS)}")
        return status

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary format."""
        task_dict = {
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date,
            "priority": self.priority,
            "status": self.status,
            "creation_timestamp": self.creation_timestamp
        }
        
        # Only include _id if it exists
        if self.id is not None:
            task_dict["_id"] = self.id
            
        return task_dict

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create a Task instance from dictionary data."""
        # Create task without validating past dates
        task = cls(
            title=data["title"],
            description=data["description"],
            due_date=data["due_date"].strftime("%Y-%m-%d %H:%M") if isinstance(data["due_date"], datetime) else data["due_date"],
            priority=data["priority"],
            status=data["status"],
            task_id=str(data["_id"]) if "_id" in data else None,
            validate_past=False  # Don't validate past dates when loading from database
        )
        task.creation_timestamp = data["creation_timestamp"]
        return task

    def __str__(self) -> str:
        """String representation of the task."""
        return (
            f"Task ID: {self.id}\n"
            f"Title: {self.title}\n"
            f"Description: {self.description}\n"
            f"Due Date: {self._format_datetime(self.due_date)}\n"
            f"Priority: {self.priority}\n"
            f"Status: {self.status}\n"
            f"Created: {self.creation_timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
        )

class TaskManager:
    def __init__(self, database):
        """Initialize task manager with database connection."""
        self.db = database

    def create_task(self, task_data: Dict[str, Any]) -> str:
        """Create a new task."""
        try:
            task = Task(
                title=task_data["title"],
                description=task_data["description"],
                due_date=task_data["due_date"],
                priority=task_data["priority"],
                status=task_data.get("status", "Pending"),
                validate_past=True  # Validate past dates for new tasks
            )
            return self.db.add_task(task.to_dict())
        except Exception as e:
            logging.error(f"Failed to create task: {str(e)}")
            raise

    def get_tasks(self, filters: Optional[Dict[str, Any]] = None) -> List[Task]:
        """Get tasks with optional filtering."""
        try:
            tasks_data = self.db.get_tasks(filters)
            return [Task.from_dict(task) for task in tasks_data]
        except Exception as e:
            logging.error(f"Failed to get tasks: {str(e)}")
            raise

    def update_task(self, task_id: str, update_data: Dict[str, Any]) -> bool:
        """Update an existing task."""
        try:
            # Convert string ID to ObjectId
            if not isinstance(task_id, ObjectId):
                try:
                    task_id = ObjectId(task_id)
                except Exception as e:
                    raise ValueError(f"Invalid task ID format: {str(e)}")

            # Validate the update data
            if "priority" in update_data:
                Task._validate_priority(update_data["priority"])
            if "status" in update_data:
                Task._validate_status(update_data["status"])
            if "due_date" in update_data:
                # Validate past dates for updates
                Task._parse_date(update_data["due_date"], validate_past=True)

            return self.db.update_task(task_id, update_data)
        except Exception as e:
            logging.error(f"Failed to update task: {str(e)}")
            raise

    def delete_task(self, task_id: str) -> bool:
        """Delete a task."""
        try:
            # Convert string ID to ObjectId
            if not isinstance(task_id, ObjectId):
                try:
                    task_id = ObjectId(task_id)
                except Exception as e:
                    raise ValueError(f"Invalid task ID format: {str(e)}")
                    
            return self.db.delete_task(task_id)
        except Exception as e:
            logging.error(f"Failed to delete task: {str(e)}")
            raise

    def mark_completed(self, task_id: str) -> bool:
        """Mark a task as completed."""
        try:
            # Convert string ID to ObjectId
            if not isinstance(task_id, ObjectId):
                try:
                    task_id = ObjectId(task_id)
                except Exception as e:
                    raise ValueError(f"Invalid task ID format: {str(e)}")
                    
            return self.db.mark_task_completed(task_id)
        except Exception as e:
            logging.error(f"Failed to mark task as completed: {str(e)}")
            raise

    def delete_all_tasks(self) -> bool:
        """Delete all tasks from the database."""
        try:
            return self.db.delete_all_tasks()
        except Exception as e:
            logging.error(f"Failed to delete all tasks: {str(e)}")
            raise 