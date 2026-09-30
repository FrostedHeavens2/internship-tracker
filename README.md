# internship-tracker

Discord bot that watches company career pages and posts matching internship/job openings.

## Companies

- **Nintendo** (Redmond, WA) — engineering/developer roles

## How it works

- Scrapes each company's careers page once per day
- Filters by location + role keywords
- Keeps a local record of seen jobs so it only posts new ones
- Posts new matches to a Discord channel via webhook

## Setup

1. Create a `.env` file (see `.env.example`):
   ```
   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
   ```
2. Install deps:
   ```
   pip install -r requirements.txt
   ```
3. Test run (won't post to Discord, prints matches):
   ```
   python tracker.py --dry-run
   ```
4. Real run (posts new matches):
   ```
   python tracker.py
   ```

## Scheduling

On Windows, use Task Scheduler to run `python tracker.py` once a day.

## Adding companies

Add a new scraper in `scrapers/` and register it in `tracker.py`.

## Filters

Edit `config.py` to change keywords, locations, or the include/exclude lists.
