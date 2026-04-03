import re
from models.schema import RequirementItem
from rules.keywords import SCORING_KEYWORDS
from rules.patterns import SCORING_SENTENCE_PATTERN


def extract_scoring_items(sections):
    results = []

    for sec in sections:
        title = sec["title"]
        content = sec["content"]
        page = sec["page"]

        if any(k in title for k in ["评分", "评标", "评审", "评分办法", "综合评分"]):
            for line in content.splitlines():
                if any(kw in line for kw in SCORING_KEYWORDS) or re.search(SCORING_SENTENCE_PATTERN, line):
                    results.append(RequirementItem(
                        category="评分项",
                        text=line.strip(),
                        source_text=line.strip(),
                        page=page,
                        priority="高",
                        is_scoring_item=True,
                        recommended_chapter="高分项重点响应"
                    ))
        else:
            for line in content.splitlines():
                if re.search(SCORING_SENTENCE_PATTERN, line):
                    results.append(RequirementItem(
                        category="评分项",
                        text=line.strip(),
                        source_text=line.strip(),
                        page=page,
                        priority="中",
                        is_scoring_item=True,
                        recommended_chapter="高分项重点响应"
                    ))
    return results
