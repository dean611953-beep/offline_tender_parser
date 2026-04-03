from parser.file_reader import extract_pdf_text, extract_docx_text
from parser.cleaner import clean_text
from parser.splitter import split_pages_to_sections
from parser.chapter_mapper import generate_chapter_suggestions

from extractors.basic_info import extract_basic_info
from extractors.dates import extract_dates_from_pages
from extractors.qualification import extract_qualification_items
from extractors.scoring import extract_scoring_items
from extractors.risks import extract_risk_items
from extractors.materials import extract_material_items
from extractors.format_rules import extract_format_items

from models.schema import AnalyzeResult


def read_file(file_path: str):
    if file_path.lower().endswith(".pdf"):
        return extract_pdf_text(file_path)
    elif file_path.lower().endswith(".docx"):
        return extract_docx_text(file_path)
    else:
        raise ValueError("暂不支持的文件类型")


def analyze_tender(file_path: str) -> AnalyzeResult:
    raw_pages = read_file(file_path)

    pages = []
    for p in raw_pages:
        pages.append({
            "page": p["page"],
            "text": clean_text(p["text"])
        })

    full_text = "\n".join([p["text"] for p in pages if p["text"]])
    sections = split_pages_to_sections(pages)

    project_info = extract_basic_info(full_text)
    dates = extract_dates_from_pages(pages)
    qualifications = extract_qualification_items(sections)
    scoring_items = extract_scoring_items(sections)
    risk_items = extract_risk_items(sections)
    material_items = extract_material_items(sections)
    format_items = extract_format_items(sections)
    chapter_suggestions = generate_chapter_suggestions()

    return AnalyzeResult(
        project_info=project_info,
        dates=dates,
        qualifications=qualifications,
        scoring_items=scoring_items,
        risk_items=risk_items,
        material_items=material_items,
        format_items=format_items,
        chapter_suggestions=chapter_suggestions,
        page_texts=pages
    )
