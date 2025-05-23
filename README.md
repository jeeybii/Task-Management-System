# Task Management Application

A Python-based task management application using MongoDB as the database.

## Features

- Add new tasks with title, description, due date, priority, and status
- List all tasks with optional filtering
- Update existing tasks
- Delete tasks
- Mark tasks as completed
- Filter tasks by various attributes

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
4. Make sure MongoDB is running on your system
5. Run the application:
   ```bash
   python main.py
   ```

## Project Structure

- `main.py`: Main application entry point
- `database.py`: Database connection and operations
- `task.py`: Task-related operations and data structures
- `requirements.txt`: Project dependencies

## Usage

The application provides a command-line interface with the following options:

1. Add Task
2. List Tasks
3. Update Task
4. Delete Task
5. Mark Task as Completed
6. Delete All Tasks
7. Exit

Follow the on-screen prompts to interact with the application.
