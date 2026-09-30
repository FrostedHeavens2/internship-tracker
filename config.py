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

# For Simplify feeds: the source already restricts to internships + new-grad and
# to your target companies. Just reject clearly non-engineering roles by title.
SIMPLIFY_EXCLUDE_KEYWORDS = [
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
