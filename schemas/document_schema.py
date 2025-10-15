from pydantic import BaseModel
from typing import Dict,Any

class ExtractedDataIn(BaseModel):
    extracted_data: Dict[str, Any]