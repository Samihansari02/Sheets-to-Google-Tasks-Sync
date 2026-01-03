from Google import Create_Service
from datetime import datetime, timezone
from dateutil import parser  # pip install python-dateutil

CLIENT_SECRET_FILE = '/Users/samihansari/Desktop/Python Project/credentials2.json'

# APIs
TASKS_API_NAME = 'tasks'
TASKS_API_VERSION = 'v1'

SHEETS_API_NAME = 'sheets'
SHEETS_API_VERSION = 'v4'

SCOPES = [
    'https://www.googleapis.com/auth/tasks',
    'https://www.googleapis.com/auth/spreadsheets.readonly'
]

# Google Sheet settings
SPREADSHEET_ID = '1BkRK5C5UTg3bzgjctVet41RVmkVo2_OVTXLC1KwyLHk'
RANGE_NAME = 'Sheet1!A1:D'  # Name, Task, DueDate, Notes

def get_or_create_tasklist(tasks_service, title: str) -> str:
    """Return tasklist id for title, create if missing."""
    resp = tasks_service.tasklists().list(maxResults=100).execute()
    for tl in resp.get("items", []):
        if tl.get("title") == title:
            return tl["id"]
    created = tasks_service.tasklists().insert(body={"title": title}).execute()
    return created["id"]

def parse_due_date(due_str: str):
    """
    Convert due date string into RFC3339 (UTC Z).
    Accepts formats like:
    - 2026-01-02
    - 02/01/2026
    - 2 Jan 2026
    - Jan 2, 2026
    """
    if not due_str or not str(due_str).strip():
        return None

    dt = parser.parse(str(due_str), dayfirst=True)  # dayfirst helps for Indian style dates
    # Google Tasks expects RFC3339, best to store as UTC midnight unless time is present
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)

    return dt.isoformat().replace("+00:00", "Z")

def main():
    # Create services
    tasks_service = Create_Service(CLIENT_SECRET_FILE, TASKS_API_NAME, TASKS_API_VERSION, SCOPES)
    sheets_service = Create_Service(CLIENT_SECRET_FILE, SHEETS_API_NAME, SHEETS_API_VERSION, SCOPES)

    # Read sheet values
    sheet = sheets_service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    values = result.get('values', [])

    if not values or len(values) < 2:
        print("No data rows found in the sheet.")
        return

    headers = [h.strip() for h in values[0]]
    # Expecting Name, Task, DueDate, Notes (Notes optional)
    # We'll map columns by header names so order can change.
    def col_idx(col_name):
        return headers.index(col_name) if col_name in headers else None

    name_i = col_idx("Name")
    task_i = col_idx("Task")
    due_i = col_idx("DueDate")
    notes_i = col_idx("Notes")  # optional

    if name_i is None or task_i is None or due_i is None:
        print("Sheet must have headers: Name, Task, DueDate (Notes optional)")
        print("Found headers:", headers)
        return

    created_count = 0

    # Iterate rows
    for row in values[1:]:
        # Safe get
        def get_cell(i):
            return row[i].strip() if i is not None and i < len(row) and row[i] else ""

        name = get_cell(name_i)
        task_title = get_cell(task_i)
        due_str = get_cell(due_i)
        notes = get_cell(notes_i) if notes_i is not None else ""

        if not name or not task_title:
            continue

        # Strategy: 1 tasklist per person name
        tasklist_id = get_or_create_tasklist(tasks_service, title=name)

        due_rfc3339 = parse_due_date(due_str)

        body = {
            "title": task_title,
        }
        if notes:
            body["notes"] = notes
        if due_rfc3339:
            body["due"] = due_rfc3339

        created = tasks_service.tasks().insert(tasklist=tasklist_id, body=body).execute()
        created_count += 1
        print(f"Created for {name}: {created.get('title')} | due: {created.get('due')}")

    print(f"\nDone. Created {created_count} tasks.")

if __name__ == "__main__":
    main()
