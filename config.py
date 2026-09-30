"""Filter config. Edit these to tune what gets posted."""

# Keywords that MUST appear in the job title (any one match qualifies)
INCLUDE_KEYWORDS = [
    "engineer",
    "developer",
    "software",
    "programmer",
    "sde",
    "swe",
]

# Keywords that DISQUALIFY a job even if it matched include (any one match rejects)
EXCLUDE_KEYWORDS = [
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
