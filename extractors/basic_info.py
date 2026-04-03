import re
from models.schema import ProjectInfo
from rules.patterns import (
    PROJECT_NAME_PATTERNS,
    TENDER_NO_PATTERNS,
    TENDER_UNIT_PATTERNS,
    BUDGET_PATTERNS
)


def _match_first(patterns, text):
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(2).strip()
    return None


def extract_basic_info(text: str) -> ProjectInfo:
    return ProjectInfo(
        project_name=_match_first(PROJECT_NAME_PATTERNS, text),
        tender_no=_match_first(TENDER_NO_PATTERNS, text),
        tender_unit=_match_first(TENDER_UNIT_PATTERNS, text),
        budget=_match_first(BUDGET_PATTERNS, text)
    )
