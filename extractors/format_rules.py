from models.schema import RequirementItem
from rules.keywords import FORMAT_KEYWORDS


def extract_format_items(sections):
    results = []
    for sec in sections:
        title = sec["title"]
        content = sec["content"]
        page = sec["page"]

        if "格式" in title or "投标文件" in title:
            for line in content.splitlines():
                if any(kw in line for kw in FORMAT_KEYWORDS):
                    results.append(RequirementItem(
                        category="格式要求",
                        text=line.strip(),
                        source_text=line.strip(),
                        page=page,
                        priority="高",
                        recommended_chapter="投标文件格式与签章检查"
                    ))
        else:
            for line in content.splitlines():
                if any(kw in line for kw in FORMAT_KEYWORDS):
                    results.append(RequirementItem(
                        category="格式要求",
                        text=line.strip(),
                        source_text=line.strip(),
                        page=page,
                        priority="中",
                        recommended_chapter="投标文件格式与签章检查"
                    ))
    return results
