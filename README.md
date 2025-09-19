# Personal Productivity App

A simple **personal productivity application** built with **FastAPI (backend)** and **HTML/CSS/JS (frontend)**.  
It includes features like task management, note-taking, and a working **Schedule Manager** with a web interface.

## Features

- **Task Management** – Organize and prioritize your tasks.
- **Note Taking** – Capture your thoughts and ideas.
- **Calendar Integration** – Sync tasks with a calendar.
- **Habit Tracking** – Monitor your habits consistently.
- **Fitness Tracker** – Track workouts and activities.
- **Schedule Manager** – Add, view, and delete events (with frontend UI).

## Prerequisites

- Python **3.9+**
- Git

## Setup & Usage

### 1. Clone the repository

```bash
git clone https://github.com/Rithesh077/personal_productivity_app
cd personal_productivity_app
```

### 2. Creat and activate a virtual environment:

```bash
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 3.Install dependencies:

```bash
pip install -r requirements.txt
```

### 4.Run the backend server:

```bash
uvicorn backend.app:app --reload
```

The API will be running at http://127.0.0.1:8000/

### 5.Open the frontend

- Go to the frontend/ folder.
- Open index.html in your browser.
- You can now add, view, and delete schedule items.

## API Endpoints:

## Features

| Method | Endpoint | Description |
| GET | `/` | App metadata + list of all features|
| GET | `/features/{id}` | Retrieve a single feature by ID |
| POST | `/features` | Add a new feature |

## Schedule Manager

| Method | Endpoint | Description |
| GET | `/schedule` | List all schedule items |
| POST | `/schedule` | Add a new schedule item |
| DELETE | `/schedule/{id}` | Delete a schedule item by ID |
