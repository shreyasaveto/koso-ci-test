# from pydantic import BaseModel, ValidationError, field_validator
# from typing import List, Optional,Dict,Any
# from datetime import datetime


# # class CustomerCreate(BaseModel):
# #     name: str
# #     pages_per_valve: int

# # class CustomerRead(BaseModel):
# #     id: int
# #     name: str
# #     organization_id: int
# #     pages_per_valve: int

# #     model_config = {
# #         "from_attributes": True
# #     }

# class OCRBox(BaseModel):
#     id: str
#     bbox: List[List[int]]
#     text: str
#     conf: float

# class BoxMapping(BaseModel):
#     key_box: List[List[float]]
#     value_box: List[List[float]]

# # class ExtractionTemplateCreate(BaseModel):
# #     name: str
# #     customer_id: int
# #     ocr_boxes: List[OCRBox]



# # class ExtractionTemplateOut(BaseModel):
# #     id: int
# #     name: str
# #     customer_id: int
# #     ocr_boxes: List[OCRBox]
# #     box_mappings: Optional[List[BoxMapping]] = None
# #     created_at: datetime

# # class ExtractedDataIn(BaseModel):
# #     extracted_data: Dict[str, Any]

# class ExtractedDataIn(BaseModel):
#     extracted_data: Dict[str, Any]