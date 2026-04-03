from pydantic import BaseModel
from typing import Optional, List


class ProjectInfo(BaseModel):
    project_name: Optional[str] = None
    tender_no: Optional[str] = None
    tender_unit: Optional[str] = None
    budget: Optional[str] = None


class DateItem(BaseModel):
    date_type: str
    value: str
    source_text: Optional[str] = None
    page: Optional[int] = None


class RequirementItem(BaseModel):
    category: str
    sub_category: Optional[str] = None
    text: str
    source_text: Optional[str] = None
    page: Optional[int] = None
    priority: str = "中"
    is_hard_requirement: bool = False
    is_scoring_item: bool = False
    is_risk_item: bool = False
    recommended_chapter: Optional[str] = None


class AnalyzeResult(BaseModel):
    project_info: ProjectInfo
    dates: List[DateItem] = []
    qualifications: List[RequirementItem] = []
    scoring_items: List[RequirementItem] = []
    risk_items: List[RequirementItem] = []
    material_items: List[RequirementItem] = []
    format_items: List[RequirementItem] = []
    chapter_suggestions: List[str] = []
    page_texts: List[dict] = []
