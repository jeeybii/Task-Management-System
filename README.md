# Task Management Application

A Python-based task management application using MongoDB as the database, featuring multithreaded operations and comprehensive task management capabilities.

## Features

- **Task Management**

  - Add new tasks with title, description, due date, priority, and status
  - Update existing tasks
  - Delete individual tasks or all tasks
  - Mark tasks as completed
  - Automatic task ID generation
  - Creation timestamp tracking

- **Advanced Task Listing**

  - List all tasks with comprehensive filtering options
  - Filter by priority (Low/Medium/High)
  - Filter by status (Pending/In Progress/Completed)
  - Filter by date range with flexible date formats
  - Case-insensitive title search
  - Display total task count for filtered results

- **Date Handling**

  - Support for both date-only (YYYY-MM-DD) and datetime (YYYY-MM-DD HH:MM) formats
  - Automatic validation of due dates
  - Flexible date range filtering with wildcard support
  - Past date validation for new tasks and updates

- **Concurrent Operations**
  - Multithreaded task processing
  - Asynchronous operation handling
  - Background task queue management
  - Thread-safe database operations

## Prerequisites

- Python 3.x
- MongoDB
- pip (Python package installer)

## Setup Instructions

1. Clone this repository
2. Install MongoDB if you haven't already
3. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables (optional):
   - Create a `.env` file with the following variables:
     ```
     MONGODB_HOST=localhost
     MONGODB_PORT=27017
     MONGODB_DATABASE=task_management
     MONGODB_COLLECTION=tasks
     LOG_LEVEL=INFO
     APP_NAME=Task Management Application
     ```
5. Make sure MongoDB is running on your system
6. Run the application:
   ```bash
   python main.py
   ```

## Project Structure

- `main.py`: Main application entry point and user interface
- `database.py`: MongoDB connection and database operations
- `task.py`: Task-related operations, data structures, and validation
- `requirements.txt`: Project dependencies
- `.env`: Environment configuration (optional)

## Usage

The application provides a command-line interface with the following options:

1. **Add Task**

   - Enter task details including title, description, due date, and priority
   - Automatic validation of all inputs
   - Support for both date and datetime formats

2. **List Tasks**

   - View all tasks or apply filters
   - Filter by priority, status, or date range
   - Use wildcards (\*) in date ranges
   - See total count of matching tasks

3. **Update Task**

   - Search by task ID or title
   - Update individual fields
   - Maintain data validation

4. **Delete Task**

   - Search by task ID or title
   - Confirmation prompt before deletion

5. **Mark Task as Completed**

   - Search by task ID or title
   - Instant status update

6. **Delete All Tasks**

   - Confirmation prompt before bulk deletion

7. **Exit**
   - Graceful shutdown of the application

## Error Handling

- Comprehensive input validation
- Detailed error messages
- Graceful error recovery
- Logging of all operations and errors

## Contributing

Feel free to submit issues and enhancement requests!
