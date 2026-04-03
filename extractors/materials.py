from models.schema import RequirementItem
from rules.keywords import MATERIAL_KEYWORDS


def extract_material_items(sections):
    results = []
    for sec in sections:
        page = sec["page"]
        for line in sec["content"].splitlines():
            if any(kw in line for kw in MATERIAL_KEYWORDS):
                results.append(RequirementItem(
                    category="材料要求",
                    text=line.strip(),
                    source_text=line.strip(),
                    page=page,
                    priority="中",
                    recommended_chapter="附件与证明材料"
                ))
    return results
