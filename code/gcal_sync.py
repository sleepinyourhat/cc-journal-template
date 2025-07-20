#!/usr/bin/env python3
"""
Google Calendar Sync Script
Fetches events from Google Calendar and saves them to markdown
"""

import os
import sys
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import argparse
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle

# If modifying these scopes, delete the token file.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

class GoogleCalendarClient:
    """Client for interacting with Google Calendar API"""
    
    def __init__(self, credentials_file='credentials.json', token_file='gcal_token.pickle'):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        self.creds = None
        self._authenticate()
    
    def _authenticate(self):
        """Handle OAuth authentication"""
        # Token file stores the user's access and refresh tokens
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                self.creds = pickle.load(token)
        
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(self.token_file, 'wb') as token:
                pickle.dump(self.creds, token)
        
        self.service = build('calendar', 'v3', credentials=self.creds)
    
    def get_calendars(self):
        """Get list of calendars"""
        try:
            calendars_result = self.service.calendarList().list().execute()
            calendars = calendars_result.get('items', [])
            return calendars
        except Exception as e:
            print(f"Error fetching calendars: {e}")
            return []
    
    def get_events(self, calendar_id='primary', time_min=None, time_max=None, max_results=100):
        """Get events from a specific calendar"""
        try:
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            events = events_result.get('items', [])
            return events
        except Exception as e:
            print(f"Error fetching events: {e}")
            return []

def format_event_time(event):
    """Format event time for display"""
    start = event.get('start', {})
    end = event.get('end', {})
    
    # Handle all-day events
    if 'date' in start:
        return f"All day"
    
    # Handle timed events
    elif 'dateTime' in start:
        start_time = datetime.fromisoformat(start['dateTime'].replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(end['dateTime'].replace('Z', '+00:00'))
        
        # Convert to local time
        start_local = start_time.astimezone()
        end_local = end_time.astimezone()
        
        # Format time
        if start_local.date() == end_local.date():
            return f"{start_local.strftime('%-I:%M %p')} - {end_local.strftime('%-I:%M %p')}"
        else:
            return f"{start_local.strftime('%b %d %-I:%M %p')} - {end_local.strftime('%b %d %-I:%M %p')}"
    
    return "No time specified"

def events_to_markdown(events, date):
    """Convert events to markdown format"""
    if not events:
        return f"# Calendar - {date}\n\nNo events scheduled.\n"
    
    markdown = f"# Calendar - {date}\n\n"
    
    # Group events by time
    all_day_events = []
    timed_events = []
    
    for event in events:
        if 'date' in event.get('start', {}):
            all_day_events.append(event)
        else:
            timed_events.append(event)
    
    # Add all-day events
    if all_day_events:
        markdown += "## All Day\n\n"
        for event in all_day_events:
            summary = event.get('summary', 'No title')
            location = event.get('location', '')
            description = event.get('description', '')
            
            markdown += f"- **{summary}**"
            if location:
                markdown += f" @ {location}"
            markdown += "\n"
            if description:
                markdown += f"  {description[:100]}{'...' if len(description) > 100 else ''}\n"
    
    # Add timed events
    if timed_events:
        if all_day_events:
            markdown += "\n"
        markdown += "## Schedule\n\n"
        
        for event in timed_events:
            summary = event.get('summary', 'No title')
            location = event.get('location', '')
            description = event.get('description', '')
            time_str = format_event_time(event)
            
            markdown += f"- **{time_str}**: {summary}"
            if location:
                markdown += f" @ {location}"
            markdown += "\n"
            if description:
                # Indent description
                desc_lines = description[:200].split('\n')
                for line in desc_lines[:3]:  # Max 3 lines
                    if line.strip():
                        markdown += f"  {line.strip()}\n"
                if len(description) > 200 or len(desc_lines) > 3:
                    markdown += "  ...\n"
    
    markdown += f"\n---\n*Synced on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}*\n"
    return markdown

def sync_calendar(client, output_dir='data', calendars_to_sync=None, days_before=3, days_ahead=7):
    """Sync calendar events to markdown files"""
    
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Get time range
    now = datetime.now(timezone.utc)
    time_min = (now - timedelta(days=days_before)).isoformat()
    time_max = (now + timedelta(days=days_ahead)).isoformat()
    
    # Get list of calendars
    calendars = client.get_calendars()
    
    if not calendars_to_sync:
        # Default to primary calendar
        calendars_to_sync = ['primary']
    
    all_events = []
    
    for cal_spec in calendars_to_sync:
        # Find calendar by ID or summary
        calendar_id = None
        calendar_name = None
        
        if cal_spec == 'primary':
            calendar_id = 'primary'
            calendar_name = 'Primary'
        else:
            for cal in calendars:
                if cal['id'] == cal_spec or cal.get('summary', '').lower() == cal_spec.lower():
                    calendar_id = cal['id']
                    calendar_name = cal.get('summary', cal['id'])
                    break
        
        if not calendar_id:
            print(f"Calendar '{cal_spec}' not found")
            continue
        
        print(f"Syncing calendar: {calendar_name}")
        
        # Get events
        events = client.get_events(
            calendar_id=calendar_id,
            time_min=time_min,
            time_max=time_max,
            max_results=100
        )
        
        # Add calendar name to each event
        for event in events:
            event['calendar_name'] = calendar_name
        
        all_events.extend(events)
    
    # Sort all events by start time
    def get_event_start(event):
        start = event.get('start', {})
        if 'dateTime' in start:
            return datetime.fromisoformat(start['dateTime'].replace('Z', '+00:00'))
        elif 'date' in start:
            return datetime.fromisoformat(start['date'] + 'T00:00:00+00:00')
        return datetime.now(timezone.utc)
    
    all_events.sort(key=get_event_start)
    
    # Create combined calendar file
    today = now.date()
    calendar_markdown = f"# Calendar - {today.strftime('%Y-%m-%d')}\n\n"
    
    # Add week overview
    for i in range(-days_before, days_ahead + 1):
        date = today + timedelta(days=i)
        day_events = [e for e in all_events if get_event_start(e).date() == date]
        
        # Highlight today
        if i == 0:
            calendar_markdown += f"## **TODAY** - {date.strftime('%A, %B %d')}\n\n"
        else:
            calendar_markdown += f"## {date.strftime('%A, %B %d')}\n\n"
        
        if not day_events:
            calendar_markdown += "No events scheduled.\n\n"
        else:
            for event in day_events:
                summary = event.get('summary', 'No title')
                time_str = format_event_time(event)
                cal_name = event.get('calendar_name', '')
                location = event.get('location', '')
                
                calendar_markdown += f"- **{time_str}**: {summary}"
                if cal_name != 'Primary':
                    calendar_markdown += f" [{cal_name}]"
                if location:
                    calendar_markdown += f" @ {location}"
                calendar_markdown += "\n"
                
                # Add description if exists and it's today
                if i == 0 and event.get('description'):
                    desc_lines = event['description'][:200].split('\n')
                    for line in desc_lines[:2]:
                        if line.strip():
                            calendar_markdown += f"  {line.strip()}\n"
        
        calendar_markdown += "\n"
    
    calendar_markdown += f"---\n*Synced on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}*\n"
    
    calendar_file = Path(output_dir) / 'calendar.md'
    with open(calendar_file, 'w') as f:
        f.write(calendar_markdown)
    print(f"Saved calendar to {calendar_file}")
    
    return len(all_events)

def main():
    parser = argparse.ArgumentParser(description="Sync Google Calendar to markdown")
    parser.add_argument("--credentials", default="credentials.json", help="Path to credentials.json file")
    parser.add_argument("--token", default="gcal_token.pickle", help="Path to token file")
    parser.add_argument("--output", default="data", help="Output directory for markdown files")
    parser.add_argument("--calendars", nargs="+", help="Calendar IDs or names to sync (default: primary)")
    parser.add_argument("--days-before", type=int, default=3, help="Number of days before today to sync (default: 3)")
    parser.add_argument("--days-ahead", type=int, default=7, help="Number of days ahead to sync (default: 7)")
    parser.add_argument("--auth", action="store_true", help="Run authentication flow")
    
    args = parser.parse_args()
    
    # Check for credentials in environment if not provided as file
    if not os.path.exists(args.credentials):
        # Check for credentials in environment variable
        creds_env = os.environ.get('GOOGLE_CALENDAR_CREDENTIALS')
        if creds_env:
            # Write credentials to temporary file
            with open(args.credentials, 'w') as f:
                f.write(creds_env)
            print("Using credentials from environment variable")
        else:
            print(f"Error: Credentials file '{args.credentials}' not found and GOOGLE_CALENDAR_CREDENTIALS not set")
            sys.exit(1)
    
    try:
        # Initialize client
        client = GoogleCalendarClient(
            credentials_file=args.credentials,
            token_file=args.token
        )
        
        if args.auth:
            print("Authentication successful!")
            print("\nAvailable calendars:")
            calendars = client.get_calendars()
            for cal in calendars:
                print(f"  - {cal.get('summary', 'Unnamed')} (ID: {cal['id']})")
            return
        
        # Sync calendars
        event_count = sync_calendar(
            client,
            output_dir=args.output,
            calendars_to_sync=args.calendars,
            days_before=args.days_before,
            days_ahead=args.days_ahead
        )
        
        print(f"\nSync completed! Found {event_count} events.")
        
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()