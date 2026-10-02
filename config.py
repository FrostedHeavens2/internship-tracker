"""Filter config. Edit these to tune what gets posted."""

# Keywords that MUST appear in the job title (any one match qualifies).
# Keep this list broad — "engineer" catches mechanical, electrical, aerospace,
# systems, controls, manufacturing, etc. Software-engineer titles are rejected
# by EXCLUDE_KEYWORDS below.
INCLUDE_KEYWORDS = [
    "engineer",
    "engineering",
]

# Keywords that DISQUALIFY a job even if it matched include (any one match rejects).
# The leading "software"/"swe"/"sde" entries filter out software roles while
# still allowing titles like "mechanical engineer", "electrical engineer",
# "aerospace engineer", "systems engineer", etc.
EXCLUDE_KEYWORDS = [
    # Software-engineering roles — not what Brandon wants
    "software engineer",
    "software developer",
    "software development engineer",
    "swe",
    "sde",
    "full stack",
    "full-stack",
    "frontend",
    "front end",
    "front-end",
    "backend",
    "back end",
    "back-end",
    "web developer",
    "mobile developer",
    "ios developer",
    "android developer",
    # Non-engineering functions
    "marketing",
    "sales",
    "business",
    "hr ",
    "human resources",
    "legal",
    "finance",
    "accounting",
    "recruiter",
    "communications",
    "translator",
    "localization",
    "ambassador",
    "retail",
    "account planner",
    "publisher developer relations",
    "structural packaging",
    "project manager",
]

# Location filter (substring match, case-insensitive). Empty list = no location filter.
LOCATIONS = ["redmond"]

# Optional: only include jobs whose title mentions "intern" (set True for intern-only mode)
INTERN_ONLY = False

# For Simplify feeds: the source already restricts to internships + new-grad and
# to your target companies. Reject clearly non-engineering roles by title, plus
# software-engineering roles (Brandon is targeting other engineering disciplines).
SIMPLIFY_EXCLUDE_KEYWORDS = [
    # Software-engineering roles
    "software engineer",
    "software developer",
    "software development engineer",
    "swe",
    "sde",
    "full stack",
    "full-stack",
    "frontend",
    "front end",
    "front-end",
    "backend",
    "back end",
    "back-end",
    "web developer",
    "mobile developer",
    "ios developer",
    "android developer",
    # Non-engineering functions
    "marketing",
    "sales",
    "business analyst",
    "business development",
    "human resources",
    "finance",
    "accounting",
    "recruiter",
    "communications",
    "legal",
    "paralegal",
    "supply chain",
    "customer",
    "helpdesk",
    "help desk",
]

# Simplify's listings are already restricted to engineering-ish roles, but
# they don't require "engineer" in the title (e.g. "Hardware Design Intern").
# This acts as a safety net alongside EXCLUDE_KEYWORDS.
