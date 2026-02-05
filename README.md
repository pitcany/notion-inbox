# Notion Inbox

A database-first logging system for Notion with FastAPI backend and CLI tool.

## Features

- **Inbox Database**: Quick capture of ideas, notes, meetings, research, and tasks
- **Daily Rollup**: Automatic linking to a daily summary page
- **FastAPI Service**: REST API for creating inbox entries
- **CLI Tool**: Command-line interface `notionw` for quick logging
- **Markdown Support**: Auto-converts Markdown-ish text to Notion blocks
- **Secure**: Only writes to configured database/page IDs from environment variables

## Setup

### 1. Create Notion Integration

1. Go to https://www.notion.so/my-integrations
2. Click "New integration"
3. Give it a name (e.g., "Notion Inbox") and select your workspace
4. Click "Submit"
5. Copy the **Internal Integration Token** (starts with `secret_`)

### 2. Share Database with Integration

**For the Inbox Database:**
1. Create a new Notion database called "Inbox" (or use existing)
2. Add these properties:
   - **Name** (title) - required
   - **Type** (select): idea, note, meeting, research, task
   - **Project** (select): Steward, Tutoring, Quant, Personal, Work
   - **Status** (select): inbox, triage, next, done
   - **Tags** (multi-select)
   - **Source** (select): ChatGPT, manual, voice, web
   - **Created** (created_time)
   - **Pinned** (checkbox)
3. Click the database menu (⋮) → "Add connections"
4. Select your integration from the list
5. **Get the Database ID**:
   - Open the database
   - Copy the URL - the database ID is the 32-character string after `/view?v=` or between `/` and `?`
   - Example: `https://www.notion.so/username/Inbox-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx?pvs=4`

**For Daily Rollup Page (optional):**
1. Create a new Notion page called "Daily Rollup"
2. Click the page menu (⋮) → "Add connections"
3. Select your integration
4. **Get the Page ID**: Same as above - it's the 32-character ID in the URL

### 3. Install and Configure

```bash
cd ~/Work/notion-inbox

# Install dependencies
bash scripts/install.sh

# Copy and edit .env file
cp .env.example .env

# Edit .env with your values:
# NOTION_TOKEN=secret_xxx...
# INBOX_DATABASE_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# DAILY_ROLLUP_PAGE_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx (optional)
```

### 4. Run the Server

```bash
# Development mode
bash scripts/run_dev.sh

# Or manually:
source .venv/bin/activate
uvicorn app.main:app --port 8787 --reload
```

## Usage

### API Endpoints

**Create inbox entry:**
```bash
curl -X POST http://127.0.0.1:8787/v1/inbox \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Review pricing strategy",
    "content": "Need to analyze competitor pricing and segment options",
    "type": "research",
    "project": "Steward",
    "tags": ["pricing", "segmentation"],
    "source": "manual",
    "also_add_to_daily_rollup": true
  }'
```

**Health check:**
```bash
curl http://127.0.0.1:8787/health
```

### CLI Tool

**Basic usage:**
```bash
notionw inbox --title "Review pricing strategy" --type research --project Steward --tags pricing,segmentation
```

**With content:**
```bash
notionw inbox --title "Meeting notes" --content "# Sales discussion\n- Budget approved\n- Timeline: Q2 launch" --project Work
```

**From stdin:**
```bash
echo "Research needed on ML models" | notionw inbox --title "Research task" --project Quant
```

**Add to daily rollup:**
```bash
notionw inbox --title "Important note" --daily
```

**Direct mode (bypasses API):**
```bash
notionw inbox --title "Quick note" --direct
```

## Recommended Workflows

### Inbox Triage
1. Quick capture everything to inbox (default status: inbox)
2. Review inbox daily, change status to triage
3. Move actionable items to next
4. Mark done items as done

### Pinned Items
Use the **Pinned** checkbox for items that need constant attention:
- Urgent tasks
- Active projects
- Important reminders

### Daily Rollup
Use `--daily` flag for items you want to track in your daily summary:
- Key decisions made
- Important conversations
- Completed milestones

## Troubleshooting

### 401 Unauthorized
- Check that `NOTION_TOKEN` in .env is correct
- Verify the integration hasn't been revoked

### Object Not Found / Missing Permission
- Ensure the database/page is shared with your integration
- Click the database/page menu → "Add connections" → select your integration
- Verify the `INBOX_DATABASE_ID` and `DAILY_ROLLUP_PAGE_ID` are correct

### Database Not Found
- The integration token must have access to the workspace containing the database
- Double-check the database ID (32 characters, hexadecimal)

### Validation Errors
- Ensure all select property values match exactly (case-sensitive)
- Check that the database has all required properties

### Content Not Appearing
- Check the daily rollup page actually has the integration connected
- Ensure the daily rollup page ID is correct in .env

### CLI Issues
- Make sure the server is running when not using `--direct` mode
- Check that `.env` file is in the project root
- Verify `NOTION_TOKEN`, `INBOX_DATABASE_ID` are set

## Project Structure

```
notion-inbox/
├── README.md
├── .gitignore
├── .env.example
├── requirements.txt
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI application & route definitions
│   ├── service.py        # Business logic (shared by API + CLI)
│   ├── notion_client.py  # Notion API client & Markdown-to-blocks converter
│   ├── models.py         # Pydantic models & enums
│   ├── exceptions.py     # Typed error hierarchy for Notion operations
│   └── settings.py       # Environment configuration
├── cli/
│   └── notionw.py        # CLI tool
└── scripts/
    ├── install.sh        # Setup virtual environment
    ├── run_dev.sh        # Run development server
    └── test_smoke.sh     # Smoke tests
```

## License

MIT
