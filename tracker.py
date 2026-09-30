"""Main entrypoint. Fetches jobs from all scrapers, filters, and posts new ones."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List

import requests
from dotenv import load_dotenv

import config
from scrapers.nintendo import Job, fetch_jobs as fetch_nintendo

SEEN_PATH = Path(__file__).with_name("seen.json")

SCRAPERS = {
    "Nintendo": fetch_nintendo,
}


def load_seen() -> dict:
    if not SEEN_PATH.exists():
        return {}
    try:
        return json.loads(SEEN_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save_seen(data: dict) -> None:
    SEEN_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def matches_filters(job: Job) -> bool:
    title_lc = job.title.lower()
    loc_lc = job.location.lower()

    if config.LOCATIONS and not any(loc in loc_lc for loc in config.LOCATIONS):
        return False

    if config.INTERN_ONLY and "intern" not in title_lc:
        return False

    if config.EXCLUDE_KEYWORDS and any(kw in title_lc for kw in config.EXCLUDE_KEYWORDS):
        return False

    if config.INCLUDE_KEYWORDS and not any(kw in title_lc for kw in config.INCLUDE_KEYWORDS):
        return False

    return True


def post_to_discord(webhook_url: str, jobs: Iterable[Job]) -> None:
    embeds = []
    for job in jobs:
        embeds.append(
            {
                "title": job.title,
                "url": job.url,
                "description": f"**{job.company}** — {job.location}\n{job.department}".strip(),
                "color": 0xE60012,  # Nintendo red-ish
            }
        )

    # Discord limits: 10 embeds per message
    for i in range(0, len(embeds), 10):
        batch = embeds[i : i + 10]
        payload = {
            "username": "Internship Tracker",
            "embeds": batch,
        }
        resp = requests.post(webhook_url, json=payload, timeout=15)
        resp.raise_for_status()


def run(dry_run: bool = False) -> int:
    load_dotenv()
    webhook = os.getenv("DISCORD_WEBHOOK_URL", "").strip()
    if not dry_run and not webhook:
        print("ERROR: DISCORD_WEBHOOK_URL is not set (see .env.example)", file=sys.stderr)
        return 2

    seen = load_seen()
    total_new: List[Job] = []

    for company, fetcher in SCRAPERS.items():
        print(f"[{company}] fetching...")
        try:
            jobs = fetcher()
        except Exception as e:
            print(f"[{company}] ERROR: {e}", file=sys.stderr)
            continue

        matched = [j for j in jobs if matches_filters(j)]
        print(f"[{company}] {len(jobs)} total, {len(matched)} match filters")

        company_seen = set(seen.get(company, []))
        new_jobs = [j for j in matched if j.job_id not in company_seen]
        print(f"[{company}] {len(new_jobs)} new")

        for j in new_jobs:
            print(f"  + {j.title} — {j.location}")

        total_new.extend(new_jobs)

        if not dry_run:
            # Only mark as seen after we've decided to post them (post first below)
            pass

        # Save the union of previously-seen and currently-matched IDs so filter
        # changes don't cause old jobs to reappear. Also include currently-matched
        # so we don't spam if the run is interrupted before posting.
        seen[company] = sorted(company_seen.union(j.job_id for j in matched))

    if dry_run:
        print(f"\n[dry-run] would post {len(total_new)} new jobs; not saving state")
        return 0

    if total_new:
        try:
            post_to_discord(webhook, total_new)
            print(f"Posted {len(total_new)} new jobs to Discord")
        except Exception as e:
            print(f"ERROR posting to Discord: {e}", file=sys.stderr)
            # Don't save state so we retry next run
            return 1

    save_seen(seen)
    print(f"Done at {datetime.now(timezone.utc).isoformat()}")
    return 0


def main() -> None:
    p = argparse.ArgumentParser(description="Track internship/job postings.")
    p.add_argument("--dry-run", action="store_true", help="Print matches without posting or saving state")
    args = p.parse_args()
    sys.exit(run(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
