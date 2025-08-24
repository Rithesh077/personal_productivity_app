# Personal Productivity API

This is a personal REST API designed to manage various productivity features like tasks, notes, and fitness tracking.

## Features

- **Task Management**: Organize and prioritize your tasks effectively.
- **Note Taking**: Capture your thoughts and ideas in a structured way.
- **Calendar Integration**: Sync your tasks with your calendar for better planning.
- **Habit Tracking**: Monitor your habits and stay consistent.
- **Fitness Tracker**: Track your workouts and physical activities.
- **Schedule Manager**: Manage your schedule efficiently.

## API Endpoints

| Method | Endpoint         | Description                          |
| ------ | ---------------- | ------------------------------------ |
| `GET`  | `/features`      | Retrieve a list of all features.     |
| `GET`  | `/features/<id>` | Retrieve a single feature by its ID. |
| `POST` | `/features`      | Add a new feature to the list        |

## How to Run Locally

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Rithesh077/personal_productivity_app
   ```
2. **Create a virtual environment(optional):**

   ```bash
   python -m venv venv
   #Windows:venv/Scripts/activate
   #macOS/Linux:source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install Flask
   ```
4. **Run the application:**
   ```bash
   python app.py
   ```
   The server will be running at `http://127.0.0.1:5000`.

## Future Enhancements

- **Frontend Integration**: Serve a web-based UI (from the `frontend/` directory) alongside the API, allowing users to interact with features visually instead of only through REST calls.
- **List all features**: Implement GET/features method to list all the existing features.
- **User Authentication**: Implement user accounts and JWT (JSON Web Tokens) for secure endpoints.
- **Database Integration**: Replace the in-memory list with a persistent database like PostgreSQL or MongoDB.
- **Full CRUD for Features**: Add `POST`, `PUT`, and `DELETE` methods to create, update, and delete features.
- **Task Management Module**: Build out the full functionality for the "Task Management" feature with its own dedicated endpoints (e.g., `/tasks`).
- **Deployment**: Deploy the application to a cloud service like Heroku or AWS.
