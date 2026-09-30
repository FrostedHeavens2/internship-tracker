"""Simplify Jobs listings scraper.

Pulls community-maintained internship + new-grad JSON feeds and filters
them by a company allowlist. Two sources:

- SimplifyJobs/Summer2026-Internships (interns)
- SimplifyJobs/New-Grad-Positions (entry-level full-time)

Each listing has: source, category, company_name, id, title, active,
terms/degrees (varies), date_updated, date_posted, url, locations,
company_url, is_visible, sponsorship.
"""

from __future__ import annotations

from typing import Iterable, List

import requests

from scrapers.nintendo import Job  # reuse the shared dataclass

INTERNSHIPS_URL = (
    "https://raw.githubusercontent.com/SimplifyJobs/"
    "Summer2026-Internships/dev/.github/scripts/listings.json"
)
NEWGRAD_URL = (
    "https://raw.githubusercontent.com/SimplifyJobs/"
    "New-Grad-Positions/dev/.github/scripts/listings.json"
)

USER_AGENT = "internship-tracker/0.1"

# Company name → set of accepted aliases (lowercased). Simplify sometimes uses
# variants like "Boeing Company" or trailing whitespace, so match loosely.
COMPANY_ALIASES: dict[str, tuple[str, ...]] = {
    "Boeing": ("boeing",),
    "Lockheed Martin": ("lockheed martin", "lockheed"),
    "RTX": ("rtx", "raytheon"),
    "Northrop Grumman": ("northrop grumman", "northrop"),
    "SpaceX": ("spacex", "space x"),
    "Blue Origin": ("blue origin",),
    "General Motors": ("general motors", "gm "),
    "Ford": ("ford motor", "ford "),
    "Toyota": ("toyota",),
    "Tesla": ("tesla",),
    "Caterpillar": ("caterpillar",),
    "John Deere": ("john deere", "deere"),
    "Cummins": ("cummins",),
    "Honeywell": ("honeywell",),
    "3M": ("3m",),
    "GE Aerospace": ("ge aerospace", "general electric aerospace"),
    "Medtronic": ("medtronic",),
    "Apple": ("apple",),
    "Amazon": ("amazon",),
    "Applied Materials": ("applied materials",),
}


def _match_company(raw_name: str) -> str | None:
    """Return canonical company name if raw_name matches any allowlisted alias."""
    name_lc = raw_name.strip().lower()
    for canonical, aliases in COMPANY_ALIASES.items():
        for alias in aliases:
            # Match on word boundaries where possible (avoid "ford" matching "stanford")
            if alias.endswith(" "):
                if name_lc.startswith(alias) or name_lc == alias.strip():
                    return canonical
            elif name_lc == alias or name_lc.startswith(alias + " ") or name_lc.endswith(" " + alias):
                return canonical
            elif alias in {"3m", "rtx", "spacex", "gm"} and alias in name_lc.split():
                return canonical
    return None


def _fetch_json(url: str, timeout: int = 30) -> list[dict]:
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


def _listing_to_job(listing: dict, canonical_company: str, kind: str) -> Job:
    locations = listing.get("locations") or []
    location = ", ".join(locations) if locations else ""
    return Job(
        company=canonical_company,
        job_id=f"simplify-{kind}-{listing.get('id', '')}",
        title=str(listing.get("title", "")).strip(),
        location=location,
        department=kind,  # "internship" or "new-grad"
        url=str(listing.get("url", "")).strip(),
    )


def _fetch_source(url: str, kind: str) -> List[Job]:
    jobs: List[Job] = []
    for listing in _fetch_json(url):
        if not listing.get("is_visible", True):
            continue
        if not listing.get("active", True):
            continue
        raw_company = str(listing.get("company_name", ""))
        canonical = _match_company(raw_company)
        if not canonical:
            continue
        jobs.append(_listing_to_job(listing, canonical, kind))
    return jobs


def fetch_jobs() -> List[Job]:
    """Fetch matching internships + new-grad roles from Simplify feeds."""
    all_jobs: List[Job] = []
    all_jobs.extend(_fetch_source(INTERNSHIPS_URL, "internship"))
    all_jobs.extend(_fetch_source(NEWGRAD_URL, "new-grad"))
    # De-dupe by (company, title, url) just in case
    seen: set[tuple[str, str, str]] = set()
    unique: List[Job] = []
    for j in all_jobs:
        key = (j.company, j.title, j.url)
        if key in seen:
            continue
        seen.add(key)
        unique.append(j)
    return unique


if __name__ == "__main__":
    for job in fetch_jobs():
        print(f"[{job.company}] {job.title} — {job.location} ({job.department})")
