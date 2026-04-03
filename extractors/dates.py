import re
from models.schema import DateItem
from rules.patterns import DATE_PATTERNS


def extract_dates_from_pages(pages):
    results = []
    seen = set()

    for page_item in pages:
        page_no = page_item["page"]
        text = page_item["text"]

        for pattern in DATE_PATTERNS:
            for match in re.finditer(pattern, text):
                key = (match.group(1), match.group(2), page_no)
                if key not in seen:
                    seen.add(key)
                    results.append(DateItem(
                        date_type=match.group(1),
                        value=match.group(2),
                        source_text=match.group(0),
                        page=page_no
                    ))
    return results
