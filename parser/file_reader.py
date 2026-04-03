import fitz
from docx import Document


def extract_pdf_text(pdf_path: str):
    doc = fitz.open(pdf_path)
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text("text")
        pages.append({
            "page": i + 1,
            "text": text.strip()
        })
    return pages


def extract_docx_text(docx_path: str):
    doc = Document(docx_path)
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    return [{
        "page": 1,
        "text": "\n".join(paragraphs)
    }]
