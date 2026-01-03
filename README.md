# Google Sheets -> Google Tasks Sync

Reads tasks from a Google Sheet and creates them in Google Tasks.
Creates one Tasklist per person (Name column).

## Sheet format
Headers required:
- Name
- Task
- DueDate
Optional:
- Notes

Example range: `Sheet1!A1:D`

## Setup
1. Create OAuth Client (Desktop app) in Google Cloud Console
2. Download the client secret JSON as `credentials.json`
3. Create a virtual environment and install deps:
   - `python -m venv .venv`
   - `source .venv/bin/activate`
   - `pip install -r requirements.txt`
4. Copy env file:
   - `cp .env.example .env`
5. Run:
   - `python src/sync_tasks.py`

## Notes
- Do not commit `credentials.json` or `token.json`
- DueDate parsing uses day-first (Indian format supported)
