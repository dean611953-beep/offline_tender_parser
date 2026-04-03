from models.schema import RequirementItem
from rules.keywords import QUALIFICATION_KEYWORDS


def extract_qualification_items(sections):
    results = []
    for sec in sections:
        title = sec["title"]
        content = sec["content"]
        page = sec["page"]

        if any(k in title for k in ["资格", "资格审查", "供应商资格", "投标人资格"]):
            lines = content.splitlines()
            for line in lines:
                if any(kw in line for kw in QUALIFICATION_KEYWORDS):
                    results.append(RequirementItem(
                        category="资格要求",
                        text=line.strip(),
                        source_text=line.strip(),
                        page=page,
                        priority="高",
                        is_hard_requirement=True,
                        recommended_chapter="公司资质与资格证明"
                    ))
        else:
            for line in content.splitlines():
                if any(kw in line for kw in QUALIFICATION_KEYWORDS):
                    results.append(RequirementItem(
                        category="资格要求",
                        text=line.strip(),
                        source_text=line.strip(),
                        page=page,
                        priority="中",
                        is_hard_requirement=True,
                        recommended_chapter="公司资质与资格证明"
                    ))
    return results
