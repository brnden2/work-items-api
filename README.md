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

Partial updates must include at least one supported field.
Explicit null values are rejected. Updated titles are trimmed before the 3-100 character length check.

Invalid updates return HTTP 422 without changing the saved record.

## Automated Tests

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

Current tests cover:

- Listing work items
- Creating and retrieving a saved work item
- Updating status while preserving the title
- Deleting a work item and confirming its removal
- Rejecting invalid titles and statuses during creation
- Rejecting invalid updates without changing saved data
- Returning 404 for a missing work item

Each test uses a fresh in-memory SQLite database, keeping tests isolated from the application's saved data.

Latest local result: 39 test cases passed.

##Search and Status Filtering

GET /work-items supports two optional query parameters:

- `q`: Case-insensitive title search, up to 100 characters.
- `status`: `open`, `in_progress` or `completed`.

Both parameters can be combined be combined. Blank searches are ignored.
Characters such as `%` and `_` are treated literally.
Results are ordered by ID. No matches return as empty list.
Invalid filter values return HTTP 422.

Examples:

- `/work-items?q=checklist`
- `/work-items?status=open`
- `/work-items?q=checklist&status=in_progress`

The frontend provides title search, status selection, Apply filters, Clear filters and Refresh results controls.

## Pagination

GET /work-items supports:

- `limit`: Records returned, default 10; allowed range 1–100.
- `offset`: Matching records skipped, default 0; minimum 0.

Search and status filters apply before pagination.
Results are ordered by ID. An offset beyond the matching records
returns an empty list. Invalid pagination parameters return HTTP 422.

Examples:

- `/work-items?limit=10&offset=0`
- `/work-items?limit=10&offset=10`
- `/work-items?status=open&limit=10&offset=0`

The frontend displays 10 records per page with Previous and Next
buttons. It requests one extra record to detect whether another
page exists. Applying or clearing filters resets to page 1.

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

## Continuous Integration (GitHub Actions)

The workflow is defined in `.github/workflows/tests.yml`.

GitHub Actions installs the project dependencies and runs the automated API tests. Workflow results are available in the repository's **Actions** tab.

Before merging changes, check that the required test run has passed. Open a failed run to inspect its logs and identify the cause.

Run the tests locally before pushing:

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

The workflow has been verified successfully on the feature branch and on `main` after merging.

## Frontend Creation Feedback

The create form prevents duplicate submissions while a request is processing.
The button displays "Creating..." and is temporarily disabled.

Successful creation clears the form and displays the new work-item ID.
Validation and connection errors display feedback while preserving the entered values.
After a connection failure, refresh the list before retrying because the request outcome may be unknown.

### Manual verification

- Loading state and disabled button checked using network throttling.
- With the backend stopped, the connection error appeared, entered values remained, and the button became usable again.
- After restarting the backend, creation succeeded and the form cleared.

Backend automated tests: 39 passed.

### Local development ports

Run the API on port 8001 when port 8000 is occupied.
The frontend API_URL must match the backend port.
The frontend runs at http://127.0.0.1:5500.

## Edit and Delete Work Items

Each work item has Edit and Delete buttons.

### Editing

Select Edit to change the title or status, then select Save changes.
Cancel closes the window without saving.

### Deletion

Select Delete to review the item's ID and title.
Select Keep work item to cancel, or Delete permanently to confirm.
Deleted items cannot be recovered through the application.

### Request Feedback

Save and delete buttons are disabled while their request is running.
If a request fails, an error message appears and the controls become
available again. Failed edits preserve the entered values.

If a connection error occurs, refresh the list after reconnecting
to check the result before retrying.

### Verification

- Existing automated API suite: 39 tests passed.
- Edited title and status remained saved after refreshing.
- Cancelling deletion preserved the item.
- Confirmed deletion removed the item after refreshing.
- API connection failure checks passed for editing and deletion.

Frontend behaviour was verified manually in the browser.