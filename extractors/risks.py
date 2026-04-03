from models.schema import RequirementItem
from rules.keywords import RISK_KEYWORDS


def extract_risk_items(sections):
    results = []
    for sec in sections:
        content = sec["content"]
        title = sec["title"]
        page = sec["page"]

        for kw in RISK_KEYWORDS:
            if kw in content:
                results.append(RequirementItem(
                    category="风险项",
                    sub_category=kw,
                    text=title,
                    source_text=content[:500],
                    page=page,
                    priority="高",
                    is_hard_requirement=True,
                    is_risk_item=True,
                    recommended_chapter="投标响应总检查"
                ))
                break
    return results
