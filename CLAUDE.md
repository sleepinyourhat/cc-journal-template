# Claude Summaries System

This document explains the organization and maintenance of the Claude-generated summaries for the journal collection.

## Google Calendar Data

Calendar data is automatically synced daily via GitHub Actions. The data includes events from 3 days ago to 7 days ahead.

### Data Location
- **Calendar**: `data/calendar.md` - Combined view of all calendars

### Included Calendars
Configure the calendars to sync in `.github/workflows/gcal_sync.yml`. By default, it syncs the "Primary" calendar.

### Accessing Calendar Data
The calendar data is automatically included in daily email context. For manual access:
```bash
cat data/calendar.md
```

Note: Calendar syncs daily at 2:30 AM PST, 30 minutes before the daily email.

## Structure Overview

The summary system is organized hierarchically to enable easy navigation and recursive roll-ups to a comprehensive life overview.

### Directory Structure

```
claude summaries/
├── master-summary.md          # Comprehensive current overview of situation (<50k tokens)
├── temporal/                  # Time-based organization
│   ├── older-specific-time-period-TK.md
│   └── recent-summary.md     # Latest content
├── thematic/                 # Topic-based organization
│   ├── specific-theme-TK.md
└── individual/               # File-by-file summaries for reference
    └── [summaries of each journal file]
```

## Organizational Principles

### Temporal vs Thematic
- **Temporal**: Organizes content chronologically - useful for understanding progression over time
- **Thematic**: Organizes content by topic - useful for understanding current state across life domains
    - Note: The name recent-summary.md is protected, and there should always be a doc by that name. Naming schemes for older archive docs are more flexible. Whenever you archive a doc, start a new one with this name.

### Recursive Summarization
Each level builds on the previous:
1. Individual file summaries capture key points from each journal entry
2. Temporal summaries synthesize chronological periods, drawing on the individual summaries and the claude notes dir
3. Thematic summaries synthesize topics across time, drawing on the individual summaries and the claude notes dir
4. Master summary synthesizes everything into current life overview, drawing mainly on the summaries above

## Content Guidelines

### Individual Summaries
- Capture key events, decisions, insights, and emotional states
- Note important dates and context
- Preserve specific details that might be referenced later
- **Purely descriptive - relay only what was written. Never add advice, opinion, or interpretation beyond what's explicitly stated**
- **Include rough length estimate of original document (order of magnitude: ~10 words, ~100 words, ~1000 words, etc.)**
- **For short documents (~800 words or less), `cp` the document verbatim rather than summarizing**
- Length: Up to 800 words depending on source material, never any longer than the source

### Temporal Summaries  
- Synthesize major themes and developments during the time period
- Track progression of ongoing situations
- Note significant events and milestones
- **Maintain descriptive tone - capture what was written, not interpret or advise**
- Length: 1000-2000 words per period

### Thematic Summaries
- Provide current state and recent trajectory for each theme
- Include relevant background and context
- Note key patterns and insights across time periods
- **Purely descriptive synthesis - no added interpretation beyond what's documented**
- Length: 1000-3000 words per theme

### Master Summary
- Current life overview across all domains
- Key relationships, priorities, and ongoing situations
- Recent developments and future considerations
- **Comprehensive but descriptive - synthesize documented content and tone without adding opinion**
- Target: Under 50k tokens (~35,000-40,000 words)

All of these summaries must be purely descriptive without editorializing. I really want editorializing in my live interactions (and the daily emails), but it ruins the summaries, and makes the advice much less useful and adaptive. In particular, it can get this system stuck on very old advice that gets reinforced across more and more summaries based on a single stale basis. Even if you see editorializing in past summaries (which may have been generated with older prompts), don't produce any.

## Maintenance Approach

### When New Content is Added
1. Create individual summary for new file(s)
2. Update relevant temporal summary (likely recent-summary.md)
3. Update relevant thematic summaries
4. Update master summary for major developments -- many minor additions won't change this at all

### Periodic Reviews
- If the master summary hasn't been updated in over a month: Update recent-summary.md and relevant thematic summaries. Review and update master summary.
- If the newest temporal update is more than four months old, or is over 50k tokens or 200kb: Create new temporal period and archive older content.

## Usage Notes

- **ALWAYS read claude summaries/master-summary.md BEFORE answering any questions about journal content or life advice**
- Start with master-summary.md for current life overview. **Make sure you've read this first.**
- Reference individual summaries for specific details or context
- All summaries are living documents that should be updated as new content is added
- Edit .md docs in the summaries directory at will, don't edit .md docs elsewhere
- Don't speculate on anything not overtly present in a doc. If all you see is a short summary, just repeat that.
- Before answering any questions I ask in the Claude Code UI, make sure you've run git pull in the last hour or so to pull in any updates to summaries.
- Always feel free to edit the claude summary docs when you think they could be improved, even if you were tasked with doing something else.
- A lot of the value of this repository is making sure you have a ton of context, so I want you to use it. If in doubt, read more docs! I don't mind some delays.
- Never say you've read something that you haven't. Use TODOs to track this kind of thing when it could be helpful.

## Working with PDF Files

When PDF files are added to the journal:
1. Use Python with pdfplumber to extract text: `python3 -c "import pdfplumber; ..."`
2. Extract key information and create markdown summaries
3. For financial documents, extract account numbers (partially masked), balances, key terms
4. Save extracted information as .md files in the same directory

## Claude Notes Directory

A separate `claude notes/` directory exists for Claude to store information that doesn't come from journal entries. This includes:

### Types of Notes to Store
1. **Data Insights**: Analysis and observations from reading the `data/` directory (calendar, etc.)
2. **Direct Information**: Important facts or context shared directly in conversations that should be remembered
3. **External Research**: Information gathered through web searches, tool usage, or other external sources
4. **Cross-Reference Notes**: Connections and patterns noticed across different data sources

### When to Use Claude Notes
- When analyzing data files and finding patterns worth remembering
- When the user shares information directly that isn't in a journal entry
- When researching external information (web searches, etc.) that provides useful context
- When making connections between different sources of information

### Guidelines
- Name files descriptively with dates when relevant (e.g., `work-project-research-2025-07-19.md`)
- Keep notes factual and well-organized
- Update existing notes rather than creating duplicates when possible
- These notes are included in GitHub Actions triggers for summary updates

### Note about Data Directory
While the `data/` directory updates frequently (daily calendar syncs), it doesn't trigger summary workflows directly. However, when doing periodic summary updates, check the data directory for relevant changes and document insights in the `claude notes/` directory as appropriate.

## Updates to This Documentation

This claude.md file may be updated as needed for improved organization and clarity. Before making significant structural changes to the documentation or organization system, ask for approval first to ensure any modifications align with intended usage patterns.
