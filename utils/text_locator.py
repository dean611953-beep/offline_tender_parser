import re
from html import escape


def split_to_paragraphs(text: str):
    if not text:
        return []
    paragraphs = [p.strip() for p in text.splitlines() if p.strip()]
    return paragraphs


def normalize_text(text: str):
    if not text:
        return ""
    text = text.strip()
    text = re.sub(r"\s+", "", text)
    return text


def find_best_paragraph(page_text: str, source_text: str = "", target_text: str = ""):
    paragraphs = split_to_paragraphs(page_text)
    if not paragraphs:
        return None, -1, []

    norm_source = normalize_text(source_text)
    norm_target = normalize_text(target_text)

    if norm_source:
        for idx, p in enumerate(paragraphs):
            if norm_source in normalize_text(p):
                return p, idx, paragraphs

    if norm_target:
        for idx, p in enumerate(paragraphs):
            if norm_target in normalize_text(p):
                return p, idx, paragraphs

    if norm_source:
        short = norm_source[:20]
        for idx, p in enumerate(paragraphs):
            if short and short in normalize_text(p):
                return p, idx, paragraphs

    if norm_target:
        short = norm_target[:20]
        for idx, p in enumerate(paragraphs):
            if short and short in normalize_text(p):
                return p, idx, paragraphs

    keywords = extract_keywords(source_text, target_text)
    best_idx = -1
    best_score = 0
    for idx, p in enumerate(paragraphs):
        score = sum(1 for kw in keywords if kw and kw in p)
        if score > best_score:
            best_score = score
            best_idx = idx

    if best_idx >= 0:
        return paragraphs[best_idx], best_idx, paragraphs

    return None, -1, paragraphs


def extract_keywords(source_text: str = "", target_text: str = ""):
    merged = f"{source_text} {target_text}"
    tokens = re.findall(r"[\u4e00-\u9fa5A-Za-z0-9\-_]{2,}", merged)
    seen = set()
    keywords = []
    for t in tokens:
        if t not in seen:
            seen.add(t)
            keywords.append(t)
    return keywords[:15]


def get_context_paragraphs(paragraphs, idx, window=2):
    if idx < 0 or not paragraphs:
        return []
    start = max(0, idx - window)
    end = min(len(paragraphs), idx + window + 1)
    result = []
    for i in range(start, end):
        result.append({
            "index": i,
            "text": paragraphs[i],
            "is_hit": i == idx
        })
    return result


def highlight_text_html(text: str, keywords: list):
    if not text:
        return ""

    html_text = escape(text)
    keywords = sorted([k for k in keywords if k], key=len, reverse=True)

    for kw in keywords:
        escaped_kw = escape(kw)
        pattern = re.escape(escaped_kw)
        html_text = re.sub(
            pattern,
            f"<mark style='background-color: #ffe58f; padding: 0 2px;'>{escaped_kw}</mark>",
            html_text,
            flags=re.IGNORECASE
        )

    return html_text
