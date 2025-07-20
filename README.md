# Claude Code Journal Template

A template repository for creating a personal journal system with Claude Code integration, automated summaries, and daily insights.

## Features

- **Automated Journal Summaries**: Claude Code automatically generates and maintains hierarchical summaries of your journal entries
- **Google Calendar Integration**: Syncs your calendar data daily for context in journal summaries and daily emails
- **Daily Email Insights**: Receive personalized daily advice based on your journal content and upcoming calendar events
- **GitHub Actions Automation**: Fully automated workflows for syncing data and updating summaries

## Directory Structure

```
├── claude summaries/          # AI-generated summaries (hierarchical)
│   ├── master-summary.md     # Comprehensive life overview
│   ├── temporal/             # Time-based summaries
│   ├── thematic/             # Topic-based summaries
│   └── individual/           # Individual file summaries
├── claude notes/             # Claude's research and insights
├── journal/                  # Your journal entries (any Claude-readable files, MD and PDF recommended)
├── data/                     # Synced calendar data
├── code/                     # Python scripts
│   ├── gcal_sync.py         # Google Calendar sync
│   └── daily_email.py       # Daily email generation
└── .github/workflows/        # GitHub Actions
```

## Setup

### 1. GitHub Secrets

Add these secrets to your repository settings:

#### Required for all features:
- `CLAUDE_API_KEY`: Your Anthropic API key
- `GITHUB_TOKEN`: Automatically available, used for summary updates

#### Required for calendar sync:
- `GOOGLE_CALENDAR_CREDENTIALS`: Your Google Calendar API credentials JSON
- `GCAL_TOKEN_DATA`: Base64-encoded OAuth token (generated automatically)

#### Required for daily emails:
- `EMAIL_SENDER`: Gmail address for sending emails
- `EMAIL_PASSWORD`: Gmail app password
- `EMAIL_RECEIVER`: Email address to receive daily insights

### 2. Google Calendar Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Google Calendar API
4. Create credentials (OAuth 2.0 Client ID for desktop application)
5. Download the credentials JSON and add to `GOOGLE_CALENDAR_CREDENTIALS` secret
6. Update the calendar list in `.github/workflows/gcal_sync.yml` to match your calendars

### 3. Environment Setup

Create a `Sendmail` environment in your GitHub repository settings with the above secrets.

## Usage

### Writing Journal Entries

1. Add markdown files to the `journal/` directory
2. Use any naming convention you prefer (dates, topics, etc.)
3. GitHub Actions will automatically generate summaries when you commit

### Calendar Integration

- Calendar data syncs daily at 2:30 AM PST
- Data is saved to `data/calendar.md`
- Includes 3 days before and 7 days ahead by default
- Configure calendars in `.github/workflows/gcal_sync.yml`

### Daily Insights

- Daily emails sent at 3 AM PST (configurable)
- Based on recent journal entries, calendar events, and life context
- Saved to `meditation advice/latest_daily_update.md`

### Summary System

The system maintains a hierarchical summary structure:

1. **Individual summaries**: Key points from each journal entry
2. **Temporal summaries**: Chronological periods (recent, quarterly, yearly)
3. **Thematic summaries**: Topics like work, health, relationships, personal growth
4. **Master summary**: Comprehensive current life overview

## Customization

### Email Content

Modify `code/daily_email.py` to change:
- Prompt for daily advice generation
- Email subject format
- Additional context sources

### Calendar Sync

Modify `code/gcal_sync.py` to change:
- Time range for events
- Calendar filtering
- Output format

### Summary Guidelines

Edit `CLAUDE.md` to customize:
- Summary structure and organization
- Content guidelines
- Maintenance approach
- Usage patterns

## Workflows

### Daily (Automated)
- Calendar sync (2:30 AM PST)
- Daily email generation (3:00 AM PST)

### Triggered by Journal Updates
- Summary generation when journal files change
- Hierarchical summary updates

### Manual
- All workflows can be triggered manually via GitHub Actions

## Troubleshooting

### Calendar Sync Issues
- Verify `GOOGLE_CALENDAR_CREDENTIALS` secret is valid JSON
- Check calendar names in workflow file match your actual calendars
- Run `python gcal_sync.py --auth` locally to test authentication

### Email Issues
- Ensure Gmail app passwords are enabled
- Verify email environment variables are set correctly
- Check spam folder for generated emails

### Summary Generation Issues
- Verify `CLAUDE_API_KEY` is valid
- Check that journal files are in markdown format
- Review GitHub Actions logs for specific errors

## License

MIT License - see LICENSE file for details.
