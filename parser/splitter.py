import re
from rules.patterns import HEADING_PATTERN


def split_pages_to_sections(pages):
    sections = []

    for page_item in pages:
        page_no = page_item["page"]
        text = page_item["text"]
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        current_title = "未命名章节"
        current_content = []

        for line in lines:
            if re.match(HEADING_PATTERN, line):
                if current_content:
                    sections.append({
                        "title": current_title,
                        "content": "\n".join(current_content),
                        "page": page_no
                    })
                current_title = line
                current_content = []
            else:
                current_content.append(line)

        if current_content:
            sections.append({
                "title": current_title,
                "content": "\n".join(current_content),
                "page": page_no
            })

    return sections
