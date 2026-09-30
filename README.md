# internship-tracker

Discord bot that watches company career pages and posts matching internship/entry-level job openings.

## Sources

- **Nintendo** careers page (Redmond, WA) — direct HTML scrape; filtered for engineering/dev roles
- **Simplify** community feeds (`SimplifyJobs/Summer2026-Internships` + `SimplifyJobs/New-Grad-Positions`)
  — filtered by an allowlist of companies (Boeing, Lockheed Martin, RTX, Northrop Grumman, SpaceX, Blue Origin,
  GM, Ford, Toyota, Tesla, Caterpillar, John Deere, Cummins, Honeywell, 3M, GE Aerospace, Medtronic,
  Apple, Amazon, Applied Materials)

## How it works

1. Fetch job listings from each source once per day.
2. Apply filters (location + role keywords for Nintendo; company allowlist + role exclusion for Simplify).
3. Compare against `seen.json` — only *new* IDs get posted.
4. Post new matches to a Discord channel via webhook, batched 10 embeds per message with a small
   inter-batch sleep to respect Discord's rate limit.

## Setup

1. Create a `.env` file (see `.env.example`):
   ```
   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
   ```
2. Install deps (Python 3.10+):
   ```
   pip install -r requirements.txt
   ```
3. **First run — seed the state** so you don't get flooded with hundreds of already-open jobs:
   ```
   python tracker.py --seed
   ```
   This marks every currently-open matching listing as "seen" without posting anything.
4. Preview what a normal run *would* post (no posting, no state save):
   ```
   python tracker.py --dry-run
   ```
5. Real run (posts new matches, saves state):
   ```
   python tracker.py
   ```

## Scheduling on Windows

Use Task Scheduler to run `tracker.py` once a day:

```powershell
schtasks /Create /TN "InternshipTracker" /TR "C:\Users\jomik\projects\internship-tracker\.venv\Scripts\python.exe C:\Users\jomik\projects\internship-tracker\tracker.py" /SC DAILY /ST 08:00
```

## Adding companies

- **Custom scraper**: add a module in `scrapers/`, expose a `fetch_jobs()` returning `List[Job]`,
  and register it in `SCRAPERS` in `tracker.py`.
- **Simplify allowlist**: add an entry to `COMPANY_ALIASES` in `scrapers/simplify.py`.

## Filters

- `config.INCLUDE_KEYWORDS` / `config.EXCLUDE_KEYWORDS` — title filters applied to Nintendo listings.
- `config.LOCATIONS` — substring location filter for Nintendo (default: Redmond).
- `config.SIMPLIFY_EXCLUDE_KEYWORDS` — title filters applied to Simplify listings
  (feeds are already restricted to your allowlisted companies + internships/new-grad, so this just
  drops obvious non-engineering roles).
