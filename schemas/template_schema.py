from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from datetime import datetime


class OCRBox(BaseModel):
    id: str
    bbox: List[List[int]]
    text: str
    conf: float

class BoxMapping(BaseModel):
    key_box: List[List[float]]
    value_box: List[List[float]]


class MappingsUpdate(BaseModel):
    box_mappings: List[BoxMapping]

class ExtractionTemplateCreate(BaseModel):
    name: str
    customer_id: int
    ocr_boxes: List[OCRBox]


class ExtractionTemplateOut(BaseModel):
    id: int
    name: str
    customer_id: int
    ocr_boxes: List[OCRBox]
    box_mappings: Optional[List[BoxMapping]] = None
    created_at: datetime


class EditTemplateDataIn(BaseModel):
    document_id: int
    ocr_boxes: List[dict]   
    box_mappings: List[dict]


