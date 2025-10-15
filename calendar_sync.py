#!/usr/bin/env python3
import json
import os
from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import pickle

SCOPES = ['https://www.googleapis.com/auth/calendar']

CREDENTIALS_FILE = 'credentials.json'  # provide your own credentials.json
TOKEN_FILE = 'token.pickle'


def load_schedule(path='schedule.json'):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_credentials():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=8080)
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    return creds


def get_service():
    creds = get_credentials()
    service = build('calendar', 'v3', credentials=creds)
    return service


def find_calendar(service, calendar_name):
    page_token = None
    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        for cal in calendar_list.get('items', []):
            if cal.get('summary') == calendar_name:
                return cal
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break
    return None


def create_calendar(service, calendar_name, timezone):
    calendar = {
        'summary': calendar_name,
        'timeZone': timezone
    }
    created = service.calendars().insert(body=calendar).execute()
    service.calendarList().insert(body={'id': created['id']}).execute()
    return created


WEEKDAY_MAP = {
    'monday': 'MO', 'tuesday': 'TU', 'wednesday': 'WE',
    'thursday': 'TH', 'friday': 'FR', 'saturday': 'SA', 'sunday': 'SU'
}


def next_date_for_weekday(weekday: int, tz):
    today = datetime.now(tz).date()
    days_ahead = weekday - today.weekday()
    if days_ahead < 0:
        days_ahead += 7
    return today + timedelta(days=days_ahead)


def create_weekly_event(service, calendar_id, title, description, weekday_str, time_str, duration_minutes, timezone, attendees, reminders):
    weekday_str_lower = weekday_str.lower()
    if weekday_str_lower not in WEEKDAY_MAP:
        raise ValueError('Invalid weekday: ' + weekday_str)
    day_code = WEEKDAY_MAP[weekday_str_lower]

    hh, mm = map(int, time_str.split(':'))
    tz = ZoneInfo(timezone)

    next_date = next_date_for_weekday(
        list(WEEKDAY_MAP.keys()).index(weekday_str_lower), tz)
    start_dt = datetime.combine(next_date, time(hh, mm), tzinfo=tz)
    end_dt = start_dt + timedelta(minutes=duration_minutes)

    event = {
        'summary': title,
        'description': description,
        'start': {
            'dateTime': start_dt.isoformat(),
            'timeZone': timezone
        },
        'end': {
            'dateTime': end_dt.isoformat(),
            'timeZone': timezone
        },
        'recurrence': [f'RRULE:FREQ=WEEKLY;BYDAY={day_code}'],
        'attendees': [{'email': em} for em in attendees],
        'reminders': {
            'useDefault': False,
            'overrides': reminders
        }
    }

    created = service.events().insert(calendarId=calendar_id,
                                      body=event, sendUpdates='all').execute()
    print(
        f"Created: {title} on {weekday_str} at {time_str} -> {created.get('htmlLink')}")
    return created


def main():
    schedule = load_schedule()
    timezone = schedule.get('timezone', 'UTC')
    calendar_name = schedule.get('calendar_name', 'Your Calendar')
    attendees = schedule.get('attendees', [])
    reminders = schedule.get('reminders', [{'method': 'popup', 'minutes': 15}])
    default_duration = schedule.get('defaults', {}).get('duration_minutes', 30)

    service = get_service()

    cal = find_calendar(service, calendar_name)
    if not cal:
        print("Calendar not found, creating it...")
        cal = create_calendar(service, calendar_name, timezone)
    cal_id = cal['id']
    print("Using calendar:", calendar_name, "id:", cal_id)

    week = schedule.get('week', {})
    for weekday, blocks in week.items():
        for slot_name, slot in blocks.items():
            time_str = slot.get('time')
            title = slot.get('title', f"{weekday.title()} {slot_name.title()}")
            desc = slot.get('description', '')
            duration = slot.get('duration_minutes', default_duration)
            create_weekly_event(service, cal_id, title, desc, weekday,
                                time_str, duration, timezone, attendees, reminders)


if __name__ == '__main__':
    main()
