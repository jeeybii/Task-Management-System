import logging
from datetime import datetime
from database import Database
from task import TaskManager, Task
import sys
import os
from dotenv import load_dotenv
from typing import Optional
from bson import ObjectId

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class TaskManagementApp:
    def __init__(self):
        """Initialize the application."""
        try:
            self.app_name = os.getenv('APP_NAME', 'Task Management Application')
            self.db = Database()
            self.task_manager = TaskManager(self.db)
        except Exception as e:
            logging.error(f"Failed to initialize application: {str(e)}")
            sys.exit(1)

    def display_menu(self):
        """Display the main menu."""
        print(f"\n{self.app_name}")
        print("1. Add Task")
        print("2. List Tasks")
        print("3. Update Task")
        print("4. Delete Task")
        print("5. Mark Task as Completed")
        print("6. Delete All Tasks")
        print("7. Exit")
        return input("Select an option (1-7): ").strip()

    def find_task(self, search_type: str) -> Optional[Task]:
        """Find a task by ID or title."""
        try:
            if search_type == "id":
                task_id = input("Enter task ID: ").strip()
                try:
                    tasks = self.task_manager.get_tasks({"_id": ObjectId(task_id)})
                except Exception as e:
                    print("Invalid task ID format")
                    return None
            else:  # search by title
                title = input("Enter task title: ").strip()
                tasks = self.task_manager.get_tasks({"title": title})

            if not tasks:
                print("No task found.")
                return None
            
            if len(tasks) > 1:
                print("\nMultiple tasks found:")
                for i, task in enumerate(tasks, 1):
                    print(f"\n{i}. Task Details:")
                    print(f"ID: {task.id}")
                    print(f"Title: {task.title}")
                    print(f"Description: {task.description}")
                    print(f"Due Date: {task.due_date.strftime('%Y-%m-%d')}")
                    print(f"Priority: {task.priority}")
                    print(f"Status: {task.status}")
                
                while True:
                    try:
                        choice = int(input("\nSelect task number: "))
                        if 1 <= choice <= len(tasks):
                            return tasks[choice - 1]
                        print("Invalid selection. Please try again.")
                    except ValueError:
                        print("Please enter a valid number.")
            
            return tasks[0]
        except Exception as e:
            logging.error(f"Failed to find task: {str(e)}")
            print(f"Error: {str(e)}")
            return None

    def add_task(self):
        """Add a new task."""
        try:
            print("\nAdd New Task")
            
            # Get and validate title
            while True:
                title = input("Title: ").strip()
                try:
                    Task._validate_title(title)
                    break
                except ValueError as e:
                    print(f"Error: {str(e)}")
            
            # Get and validate description
            while True:
                description = input("Description: ").strip()
                try:
                    Task._validate_description(description)
                    break
                except ValueError as e:
                    print(f"Error: {str(e)}")
            
            # Get and validate due date
            while True:
                try:
                    due_date = input("Due Date (YYYY-MM-DD): ").strip()
                    Task._parse_date(due_date)
                    break
                except ValueError as e:
                    print(f"Error: {str(e)}")
            
            # Get and validate priority
            while True:
                try:
                    priority = input("Priority (Low/Medium/High): ").strip()
                    Task._validate_priority(priority)
                    break
                except ValueError as e:
                    print(f"Error: {str(e)}")
            
            task_data = {
                "title": title,
                "description": description,
                "due_date": due_date,
                "priority": priority
            }
            
            task_id = self.task_manager.create_task(task_data)
            print(f"\nTask created successfully!")
            print(f"Task ID: {task_id}")
            print(f"Title: {title}")
            print(f"Description: {description}")
            print(f"Due Date: {due_date}")
            print(f"Priority: {priority}")
        except Exception as e:
            logging.error(f"Failed to add task: {str(e)}")
            print(f"Error: {str(e)}")

    def list_tasks(self):
        """List all tasks with optional filtering."""
        try:
            print("\nList Tasks")
            print("Filter options:")
            print("1. All tasks")
            print("2. By priority")
            print("3. By status")
            print("4. By due date range")
            
            choice = input("Select filter option (1-4): ").strip()
            filters = {}
            
            if choice == "2":
                while True:
                    priority = input("Enter priority (Low/Medium/High): ").strip()
                    try:
                        # Convert to title case for consistent comparison
                        priority = priority.capitalize()
                        Task._validate_priority(priority)
                        filters["priority"] = priority
                        break
                    except ValueError as e:
                        print(f"Error: {str(e)}")
            elif choice == "3":
                while True:
                    status = input("Enter status (Pending/In Progress/Completed): ").strip()
                    try:
                        Task._validate_status(status)
                        filters["status"] = status
                        break
                    except ValueError as e:
                        print(f"Error: {str(e)}")
            elif choice == "4":
                print("\nEnter date range (YYYY-MM-DD format)")
                print("Use * to leave either From or To date blank")
                print("Example: From: 2024-01-01, To: * (shows all tasks from 2024-01-01 onwards)")
                print("Example: From: *, To: 2024-12-31 (shows all tasks up to 2024-12-31)")
                
                while True:
                    try:
                        # Get and validate From date
                        from_date = input("From date: ").strip()
                        if from_date == "*":
                            from_date_parsed = None
                        else:
                            from_date_parsed = Task._parse_filter_date(from_date)
                        
                        # Get and validate To date
                        to_date = input("To date: ").strip()
                        if to_date == "*":
                            to_date_parsed = None
                        else:
                            to_date_parsed = Task._parse_filter_date(to_date)
                        
                        # Validate that at least one date is provided
                        if from_date == "*" and to_date == "*":
                            print("\nError: At least one date must be provided!")
                            print("Please enter at least one date or use * for the other.")
                            continue
                        
                        # Validate date range if both dates are provided
                        if from_date != "*" and to_date != "*":
                            if from_date_parsed > to_date_parsed:
                                print("\nError: Invalid date range!")
                                print(f"From date ({from_date_parsed.strftime('%Y-%m-%d')}) cannot be after To date ({to_date_parsed.strftime('%Y-%m-%d')})")
                                print("Please enter the dates again.")
                                continue
                        
                        # Set the date range filter
                        filters["due_date"] = {}
                        if from_date != "*":
                            filters["due_date"]["$gte"] = from_date_parsed
                        if to_date != "*":
                            filters["due_date"]["$lte"] = to_date_parsed
                        
                        # Display search range
                        range_description = "Searching for tasks"
                        if from_date != "*" and to_date != "*":
                            range_description += f" between {from_date_parsed.strftime('%Y-%m-%d')} and {to_date_parsed.strftime('%Y-%m-%d')}"
                        elif from_date != "*":
                            range_description += f" from {from_date_parsed.strftime('%Y-%m-%d')} onwards"
                        elif to_date != "*":
                            range_description += f" up to {to_date_parsed.strftime('%Y-%m-%d')}"
                        print(f"\n{range_description}")
                        break
                    except ValueError as e:
                        print(f"Error: {str(e)}")
                        print("Please enter valid dates in YYYY-MM-DD format or * for wildcard.")
            
            tasks = self.task_manager.get_tasks(filters)
            
            if not tasks:
                print("\nNo tasks found.")
                return
            
            print("\nTasks:")
            for task in tasks:
                print(f"\nID: {task.id}")
                print(f"Title: {task.title}")
                print(f"Description: {task.description}")
                print(f"Due Date: {task.due_date.strftime('%Y-%m-%d')}")
                print(f"Priority: {task.priority}")
                print(f"Status: {task.status}")
                print(f"Created: {task.creation_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        except Exception as e:
            logging.error(f"Failed to list tasks: {str(e)}")
            print(f"Error: {str(e)}")

    def update_task(self):
        """Update an existing task."""
        try:
            print("\nUpdate Task")
            print("Search by:")
            print("1. Task ID")
            print("2. Task Title")
            
            search_choice = input("Select search option (1-2): ").strip()
            search_type = "id" if search_choice == "1" else "title"
            
            task = self.find_task(search_type)
            if not task:
                return
            
            print("\nCurrent task details:")
            print(f"ID: {task.id}")
            print(f"Title: {task.title}")
            print(f"Description: {task.description}")
            print(f"Due Date: {task.due_date.strftime('%Y-%m-%d')}")
            print(f"Priority: {task.priority}")
            print(f"Status: {task.status}")
            
            print("\nUpdate options:")
            print("1. Title")
            print("2. Description")
            print("3. Due Date")
            print("4. Priority")
            print("5. Status")
            
            choice = input("Select field to update (1-5): ").strip()
            update_data = {}
            
            if choice == "1":
                update_data["title"] = input("New title: ").strip()
            elif choice == "2":
                update_data["description"] = input("New description: ").strip()
            elif choice == "3":
                while True:
                    try:
                        due_date = input("New due date (YYYY-MM-DD): ").strip()
                        Task._parse_date(due_date)
                        update_data["due_date"] = due_date
                        break
                    except ValueError as e:
                        print(f"Error: {str(e)}")
            elif choice == "4":
                while True:
                    try:
                        priority = input("New priority (Low/Medium/High): ").strip()
                        Task._validate_priority(priority)
                        update_data["priority"] = priority
                        break
                    except ValueError as e:
                        print(f"Error: {str(e)}")
            elif choice == "5":
                while True:
                    try:
                        status = input("New status (Pending/In Progress/Completed): ").strip()
                        Task._validate_status(status)
                        update_data["status"] = status
                        break
                    except ValueError as e:
                        print(f"Error: {str(e)}")
            
            if self.task_manager.update_task(task.id, update_data):
                print("Task updated successfully")
            else:
                print("Failed to update task")
        except Exception as e:
            logging.error(f"Failed to update task: {str(e)}")
            print(f"Error: {str(e)}")

    def delete_task(self):
        """Delete a task."""
        try:
            print("\nDelete Task")
            print("Search by:")
            print("1. Task ID")
            print("2. Task Title")
            
            search_choice = input("Select search option (1-2): ").strip()
            search_type = "id" if search_choice == "1" else "title"
            
            task = self.find_task(search_type)
            if not task:
                return
            
            print("\nTask to delete:")
            print(f"ID: {task.id}")
            print(f"Title: {task.title}")
            print(f"Description: {task.description}")
            print(f"Due Date: {task.due_date.strftime('%Y-%m-%d')}")
            print(f"Priority: {task.priority}")
            print(f"Status: {task.status}")
            
            confirm = input("\nAre you sure you want to delete this task? (yes/no): ").strip().lower()
            if confirm == "yes":
                if self.task_manager.delete_task(task.id):
                    print("Task deleted successfully")
                else:
                    print("Failed to delete task")
            else:
                print("Deletion cancelled")
        except Exception as e:
            logging.error(f"Failed to delete task: {str(e)}")
            print(f"Error: {str(e)}")

    def mark_completed(self):
        """Mark a task as completed."""
        try:
            print("\nMark Task as Completed")
            print("Search by:")
            print("1. Task ID")
            print("2. Task Title")
            
            search_choice = input("Select search option (1-2): ").strip()
            search_type = "id" if search_choice == "1" else "title"
            
            task = self.find_task(search_type)
            if not task:
                return
            
            if self.task_manager.mark_completed(task.id):
                print("Task marked as completed")
            else:
                print("Failed to mark task as completed")
        except Exception as e:
            logging.error(f"Failed to mark task as completed: {str(e)}")
            print(f"Error: {str(e)}")

    def delete_all_tasks(self):
        """Delete all tasks from the database."""
        try:
            print("\nDelete All Tasks")
            print("WARNING: This action cannot be undone!")
            print("All tasks will be permanently deleted.")
            
            confirm = input("\nAre you sure you want to delete ALL tasks? (yes/no): ").strip().lower()
            if confirm == "yes":
                if self.task_manager.delete_all_tasks():
                    print("All tasks have been deleted successfully")
                else:
                    print("No tasks were found to delete")
            else:
                print("Operation cancelled")
        except Exception as e:
            logging.error(f"Failed to delete all tasks: {str(e)}")
            print(f"Error: {str(e)}")

    def run(self):
        """Run the application."""
        while True:
            choice = self.display_menu()
            
            if choice == "1":
                self.add_task()
            elif choice == "2":
                self.list_tasks()
            elif choice == "3":
                self.update_task()
            elif choice == "4":
                self.delete_task()
            elif choice == "5":
                self.mark_completed()
            elif choice == "6":
                self.delete_all_tasks()
            elif choice == "7":
                print("Goodbye!")
                self.db.close()
                break
            else:
                print("Invalid option. Please try again.")

if __name__ == "__main__":
    app = TaskManagementApp()
    app.run() 