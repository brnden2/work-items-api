# Database Backup and Recovery Guide

## Purpose

Back up the Work Items API SQLite database and verify recovery using

a separate test database.

Run these commands in PowerShell from the project folder.

Keep the same PowerShell window open so the variables remain available.

## 1. Confirm the database

This guide assumes the configured database is `work_items.db`.

If DATABASE_URL points elsewhere, use that database's actual path.

```powershell
Get-Item .\work_items.db
```

## 2. Stop the application

Press Ctrl+C in the API server window.

Ensure all applications using this database have stopped before

copying it. For a running database, use SQLite's backup API instead

of this file-copy procedure.

## 3. Create a backup

```powershell
New-Item -ItemType Directory -Path .\backups -Force
$backupFile = ".\backups\work_items_$(Get-Date -Format 'yyyyMMdd_HHmmss_fff').db"
Copy-Item -LiteralPath .\work_items.db -Destination $backupFile
```

Compare the files:

```powershell
Get-FileHash -LiteralPath .\work_items.db, $backupFile |
    Select-Object Path, Hash |
    Format-List
```

Both SHA-256 hashes should match.

The backups folder is useful for recovery practice. Maintain another

copy in an approved backup location to protect against laptop failure.

## 4. Restore into a separate test database

```powershell
$restoreFile = ".\backups\restore_test_$(Get-Date -Format 'yyyyMMdd_HHmmss_fff').db"
Copy-Item -LiteralPath $backupFile -Destination $restoreFile
```

This leaves the original database unchanged.

## 5. Verify database integrity and records

Paste the entire block into PowerShell:

```powershell
@'
import sqlite3
import sys
from pathlib import Path
def read_database(filename):
    path = Path(filename).resolve()
    with sqlite3.connect(path.as_uri() + "?mode=ro", uri=True) as connection:
        integrity = connection.execute("PRAGMA integrity_check").fetchall()
        records = connection.execute(
            "SELECT * FROM workitem ORDER BY id"
        ).fetchall()
    return integrity, records
original_integrity, original = read_database("work_items.db")
restored_integrity, restored = read_database(sys.argv[1])
print("Original integrity:", original_integrity)
print("Restored integrity:", restored_integrity)
print("Original records:", len(original))
print("Restored records:", len(restored))
print("Records match:", original == restored)
if original_integrity != [("ok",)] or restored_integrity != [("ok",)]:
    raise SystemExit("Integrity verification failed.")
if original != restored:
    raise SystemExit("Record comparison failed.")
'@ | .\.venv\Scripts\python.exe - $restoreFile
```

Expected results:

- Both integrity checks return `[('ok',)]`.

- Record counts match.

- Records match is `True`.

Record counts depend on the database being backed up.

## 6. Test the restored database through the API

Save the previous setting and start the test server:

```powershell
$previousDatabaseUrl = $env:DATABASE_URL
$env:DATABASE_URL = "sqlite:///" + (Resolve-Path $restoreFile).Path.Replace('\', '/')
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8001
```

Open http://127.0.0.1:8001/docs.

Execute GET /work-items and confirm:

- HTTP response is 200.

- Returned records agree with the restored database.

## 7. Restore the normal configuration

Press Ctrl+C to stop the test server.

In the same PowerShell window:

```powershell
if ($null -eq $previousDatabaseUrl) {
    Remove-Item Env:DATABASE_URL -ErrorAction SilentlyContinue
} else {
    $env:DATABASE_URL = $previousDatabaseUrl
}
```

The test database can be retained as evidence. This procedure does not

replace the original database.

## 8. Keep databases out of Git

Ensure `.gitignore` includes:

```gitignore
*.db
```

Check:

```powershell
git status --short
git ls-files "*.db"
```

No database files should appear as tracked files.

Keep database backups private.

## Recorded Recovery Practice

On 08 October 2026:

- Backup and original SHA-256 hashes matched.

- Restored database integrity returned `ok`.

- All four work-item records matched.

- GET /work-items returned HTTP 200 using the restored database.

- No database files were tracked by Git.
