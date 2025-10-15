# Calendar Sync App 

A minimal, sanitized template for a Python app that syncs a weekly JSON schedule to Google Calendar and sends invites/reminders.

What this template contains
- `calendar_sync.py` — sanitized script (no credentials or emails).
- `credentials.example.json` — example OAuth client file (placeholders only).
- `schedule.example.json` — example schedule structure.
- `.gitignore` — ignores local secrets and tokens.

Quick start
1. Copy `credentials.example.json` to `credentials.json` and fill in your OAuth client values (use a Desktop OAuth client or add test users).
2. Copy `schedule.example.json` to `schedule.json` and fill in your timezone, calendar_name, and week entries.
3. Install dependencies: `pip install -r requirements.txt` (or at least `google-auth-oauthlib google-api-python-client tzdata`).
4. Run: `python calendar_sync.py`

Notes
- This repository is a template: do NOT commit `credentials.json` or any real emails here.
- Use the private repository to store your full project with `credentials.json` and any private data.

Suggested GitHub repo description (short):
"Sync weekly schedules to Google Calendar with invites & reminders (template)."

Suggested long description for the GitHub repo page:
"A lightweight Python utility that reads a JSON schedule and creates recurring weekly events in Google Calendar, sending invites and reminders to attendees. This repository is a sanitized template — replace `credentials.example.json` and `schedule.example.json` with your own `credentials.json` and `schedule.json` before running."

Suggested topics/tags: google-calendar, oauth, python, schedule, template
