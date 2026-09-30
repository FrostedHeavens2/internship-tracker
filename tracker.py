"""Main entrypoint. Fetches jobs from all scrapers, filters, and posts new ones."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List

import requests
from dotenv import load_dotenv

import config
from scrapers.nintendo import Job, fetch_jobs as fetch_nintendo
from scrapers.simplify import fetch_jobs as fetch_simplify

SEEN_PATH = Path(__file__).with_name("seen.json")

# Each entry is (bucket_name, fetcher, uses_local_filters)
# - Nintendo: scraped directly, filter with config.INCLUDE/EXCLUDE keywords
# - Simplify: already company-filtered inside the scraper; it also intrinsically
#   restricts to internships + new-grad roles, so we skip the keyword filter
SCRAPERS = [
    ("Nintendo", fetch_nintendo, True),
    ("Simplify", fetch_simplify, False),
]


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


def matches_simplify_filters(job: Job) -> bool:
    """Lighter filter for Simplify listings: they're already company + intern/new-grad
    filtered upstream, but we still reject roles we clearly don't want."""
    title_lc = job.title.lower()
    if any(kw in title_lc for kw in config.SIMPLIFY_EXCLUDE_KEYWORDS):
        return False
    return True


def post_to_discord(webhook_url: str, jobs: Iterable[Job]) -> None:
    embeds = []
    for job in jobs:
        # Truncate location if absurdly long (Discord field limits)
        location = job.location if len(job.location) <= 200 else job.location[:197] + "..."
        desc = f"**{job.company}** — {location}"
        if job.department:
            desc += f"\n_{job.department}_"
        embeds.append(
            {
                "title": job.title[:256],
                "url": job.url,
                "description": desc[:4096],
                "color": 0xE60012,
            }
        )

    # Discord limits: 10 embeds per message, ~30 req/min per webhook.
    # Sleep 2.5s between batches to stay comfortably under the rate limit.
    batch_size = 10
    for i in range(0, len(embeds), batch_size):
        batch = embeds[i : i + batch_size]
        payload = {
            "username": "Internship Tracker",
            "embeds": batch,
        }
        resp = requests.post(webhook_url, json=payload, timeout=15)
        if resp.status_code == 429:
            retry_after = float(resp.json().get("retry_after", 5))
            print(f"  Rate limited, sleeping {retry_after:.1f}s", file=sys.stderr)
            time.sleep(retry_after + 0.5)
            resp = requests.post(webhook_url, json=payload, timeout=15)
        resp.raise_for_status()
        if i + batch_size < len(embeds):
            time.sleep(2.5)


def run(dry_run: bool = False, seed_only: bool = False) -> int:
    load_dotenv()
    webhook = os.getenv("DISCORD_WEBHOOK_URL", "").strip()
    if not dry_run and not seed_only and not webhook:
        print("ERROR: DISCORD_WEBHOOK_URL is not set (see .env.example)", file=sys.stderr)
        return 2

    seen = load_seen()
    total_new: List[Job] = []

    for bucket, fetcher, use_local_filters in SCRAPERS:
        print(f"[{bucket}] fetching...")
        try:
            jobs = fetcher()
        except Exception as e:
            print(f"[{bucket}] ERROR: {e}", file=sys.stderr)
            continue

        if use_local_filters:
            matched = [j for j in jobs if matches_filters(j)]
        else:
            matched = [j for j in jobs if matches_simplify_filters(j)]
        print(f"[{bucket}] {len(jobs)} total, {len(matched)} match filters")

        bucket_seen = set(seen.get(bucket, []))
        new_jobs = [j for j in matched if j.job_id not in bucket_seen]
        print(f"[{bucket}] {len(new_jobs)} new")

        for j in new_jobs:
            print(f"  + [{j.company}] {j.title} — {j.location}")

        total_new.extend(new_jobs)

        # Save the union of previously-seen and currently-matched IDs so filter
        # changes don't cause old jobs to reappear. Include currently-matched
        # regardless of posting result to avoid re-spamming on interrupted runs.
        seen[bucket] = sorted(bucket_seen.union(j.job_id for j in matched))

    if dry_run:
        print(f"\n[dry-run] would post {len(total_new)} new jobs; not saving state")
        return 0

    if seed_only:
        save_seen(seen)
        print(
            f"\n[seed] marked {len(total_new)} currently-open jobs as seen; "
            f"future runs will only post new ones. State saved to {SEEN_PATH.name}"
        )
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
    p.add_argument(
        "--seed",
        action="store_true",
        help="Mark all currently-open matches as seen without posting; use on first run",
    )
    args = p.parse_args()
    sys.exit(run(dry_run=args.dry_run, seed_only=args.seed))


if __name__ == "__main__":
    main()
