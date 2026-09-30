"""Nintendo careers scraper.

The Nintendo careers site renders all open roles on a single page as plain HTML
(anchors linking to /jobs/<id>/), which makes scraping cheap and reliable.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List

import requests
from bs4 import BeautifulSoup

JOBS_URL = "https://careers.nintendo.com/jobs/"
JOB_LINK_RE = re.compile(r"^/jobs/(\d+)/?$")

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) internship-tracker/0.1"
)

_CONTROL_RE = re.compile(r"[\uE000-\uF8FF\u200B-\u200D\uFEFF]+")


def _clean(text: str) -> str:
    return _CONTROL_RE.sub("", text).strip()


@dataclass(frozen=True)
class Job:
    company: str
    job_id: str
    title: str
    location: str
    department: str
    url: str


def fetch_jobs(timeout: int = 20) -> List[Job]:
    """Fetch and parse all Nintendo job postings.

    Each job is rendered as an <a class="job-card_card__..." href="/jobs/<id>/">
    containing an <h3> title and two detail <span>s (location, department).
    """
    resp = requests.get(JOBS_URL, headers={"User-Agent": USER_AGENT}, timeout=timeout)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    jobs: List[Job] = []
    for a in soup.find_all("a", href=JOB_LINK_RE):
        job_id_match = JOB_LINK_RE.match(a["href"])
        if not job_id_match:
            continue
        job_id = job_id_match.group(1)

        h3 = a.find("h3")
        title = h3.get_text(strip=True) if h3 else a.get_text(" ", strip=True)
        if not title:
            continue

        detail_spans = a.select("div.job-card_card__details__wISJ0 span")
        # Strip stray control chars (page uses a private-use glyph after some labels)
        details = [_clean(s.get_text(strip=True)) for s in detail_spans]
        location = details[0] if len(details) > 0 else ""
        department = details[1] if len(details) > 1 else ""

        jobs.append(
            Job(
                company="Nintendo",
                job_id=job_id,
                title=_clean(title),
                location=location,
                department=department,
                url=f"https://careers.nintendo.com/jobs/{job_id}/",
            )
        )

    # De-duplicate by job_id (site sometimes repeats anchors)
    seen_ids: set[str] = set()
    unique: List[Job] = []
    for j in jobs:
        if j.job_id in seen_ids:
            continue
        seen_ids.add(j.job_id)
        unique.append(j)
    return unique


if __name__ == "__main__":
    for job in fetch_jobs():
        print(f"[{job.job_id}] {job.title} — {job.location} — {job.department}")
