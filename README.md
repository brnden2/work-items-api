# Work Items API

A small full-stack project built with FastAPI, SQLModel, SQLite, HTML and JavaScript.

The project demonstrates frontend-to-API communication, validation, database persistence, configuration management and automated API testing.

## Architecture

```text
Browser
   ↓
HTML + JavaScript
   ↓
Fetch API
   ↓
FastAPI
   ↓
SQLModel
   ↓
SQLite
```

## Project Structure

```text
work-items-api/
│
├── config.py
├── database.py
├── main.py
├── models.py
├── requirements.txt
├── .env.example
├── .gitignore
│
├── frontend/
│   ├── index.html
│   └── script.js
│
└── tests/
    └── test_api.py
```

## Setup

### 1. Create a virtual environment

```powershell
python -m venv .venv
```

### 2. Install dependencies

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 3. Create the environment file

```powershell
Copy-Item .env.example .env
```

The default configuration is:

```env
DATABASE_URL=sqlite:///work_items.db
FRONTEND_ORIGINS=http://127.0.0.1:5500,http://localhost:5500
```

### 4. Start the FastAPI backend

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

### 5. Start the frontend

Open another terminal:

```powershell
cd frontend
python -m http.server 5500
```

Frontend:

```text
http://127.0.0.1:5500
```

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/work-items` | Get all work items |
| GET | `/work-items/{id}` | Get one work item |
| POST | `/work-items` | Create a work item |
| PATCH | `/work-items/{id}` | Update a work item |
| DELETE | `/work-items/{id}` | Delete a work item |

## Validation

Work-item titles must contain between 3 and 100 characters.

Allowed status values:

```text
open
in_progress
completed
```

## Automated Tests

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

Current tests cover:

- GET work items
- title validation
- status validation
- 404 handling

## Configuration

Application configuration is stored outside the application code.

```text
.env
 ↓
config.py
 ├── database.py
 └── main.py
```

The `.env` file is excluded from Git.

`.env.example` provides the configuration template required to set up the project.