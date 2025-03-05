# File Processing System

A Django-based system that allows users to login, submit files, and process them using Celery tasks.

## Features

- User Authentication
- File Upload System
- Asynchronous Task Processing with Celery
- Task Status Tracking
- Secure File Management

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up Redis (required for Celery):
   - Install Redis on your system
   - Ensure Redis server is running

4. Environment Variables:
   Create a `.env` file in the project root with:
   ```
   SECRET_KEY=your_secret_key
   DEBUG=True
   REDIS_URL=redis://localhost:6379/0
   ```

5. Initialize the database:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```bash
   python manage.py runserver
   ```

7. Start Celery worker:
   ```bash
   celery -A file_processor worker -l info
   ```

## Project Structure

- `file_processor/` - Main Django project directory
- `users/` - User authentication and management
- `files/` - File upload and management
- `tasks/` - Celery tasks and task management
- `templates/` - HTML templates
- `static/` - Static files (CSS, JS, etc.)

## Usage

1. Register/Login through the web interface
2. Upload files through the dashboard
3. Select files and choose processing actions
4. Monitor task progress in real-time
5. Download processed results
