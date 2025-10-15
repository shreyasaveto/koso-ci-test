from fastapi import APIRouter, UploadFile, File, Depends, Form

from auth.token import get_current_user
from models.models import User
from services.ocr_services import process_ocr, process_kv_extraction

router = APIRouter(include_in_schema=False)


@router.post("/ocr-extract/")
async def ocr_extract(pdf: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    return await process_ocr(pdf)


@router.post("/apply-kv-on-pdf/")
async def apply_kv_on_pdf(
        pdf: UploadFile = File(...),
        key_value_boxes: str = Form(...),
        current_user: User = Depends(get_current_user)
):
    return await process_kv_extraction(pdf, key_value_boxes)
