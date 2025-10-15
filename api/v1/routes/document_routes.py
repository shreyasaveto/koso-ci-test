import io
import json
import pandas as pd
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Body
from sqlalchemy.orm import Session
from starlette.responses import StreamingResponse

from auth.token import get_current_user
from db.database import get_db
from models.models import User, Customer, Document, ExtractionTemplate
# from backend.api.v1.routes.routes import ExtractedDataIn
from schemas.document_schema import ExtractedDataIn
from services.document_service import create_document

router = APIRouter()


# @router.post("/save-doc/")
# async def upload_document(
#         pdf: UploadFile = File(...),
#         customer_id: int = Form(...),
#         template_id: int | None = Form(None),
#         db: Session = Depends(get_db),
#         current_user: User = Depends(get_current_user),  # Add user dependency
# ):
#     # Validate PDF file type
#     if pdf.content_type != "application/pdf":
#         raise HTTPException(status_code=400, detail="Only PDF files are allowed")

#     # Check if customer exists and belongs to current user's organization
#     customer = db.query(Customer).filter_by(
#         id=customer_id,
#         organization_id=current_user.organization_id
#     ).first()
#     if not customer:
#         raise HTTPException(status_code=403, detail="You are not authorized to upload documents for this customer.")

#     # If template_id provided, check if template exists and belongs to the same customer
#     if template_id is not None:
#         template = db.query(ExtractionTemplate).filter_by(
#             id=template_id,
#             customer_id=customer_id
#         ).first()
#         if not template:
#             raise HTTPException(status_code=400, detail="Invalid template_id for this customer.")

#     pdf_bytes = await pdf.read()

#     doc = Document(
#         customer_id=customer_id,
#         uploaded_by_user_id=current_user.id,  # Use current user as uploader
#         filename=pdf.filename,
#         raw_pdf=pdf_bytes,
#         template_id=template_id,
#         uploaded_at=datetime.utcnow(),
#     )

#     db.add(doc)
#     db.commit()
#     db.refresh(doc)

#     return {
#         "document_id": doc.id,
#         "message": "PDF uploaded successfully",
#         "filename": doc.filename
#     }


@router.post("/add/",include_in_schema=True)
async def upload_document(
    pdf: UploadFile = File(...),
    customer_id: int = Form(...),
    project_id: int = Form(...),
    template_name: str = Form(...),
    format_id: int = Form(...),
    fluid_state_id: int = Form(...),
    page_per_item: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await create_document(
        pdf=pdf,
        customer_id=customer_id,
        project_id=project_id,
        format_id=format_id,
        fluid_state_id=fluid_state_id,
        template_name = template_name,
        page_per_item=page_per_item,
        db=db,
        current_user=current_user
    )



@router.patch("/save-extracted-data/{document_id}/",include_in_schema=False)
def save_extracted_data(
        document_id: int,
        payload: ExtractedDataIn,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),  # Add user dependency
):
    doc = db.query(Document).filter_by(id=document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Check if document's customer belongs to current user's organization
    if doc.customer.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="You are not authorized to modify this document.")

    doc.extracted_data = payload.extracted_data
    db.commit()
    db.refresh(doc)

    return {
        "message": "Extracted data saved successfully",
        "document_id": doc.id
    }


@router.get("/documents/{document_id}/",include_in_schema=False)
def get_document(
        document_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    doc = db.query(Document).filter_by(id=document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Check organization access
    if doc.customer.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return {
        "id": doc.id,
        "filename": doc.filename,
        "uploaded_at": doc.uploaded_at.isoformat(),
        "template_id": doc.template_id,
        "extracted_data": doc.extracted_data,
        "customer_id": doc.customer_id,
        "uploaded_by_user_id": doc.uploaded_by_user_id,
    }


@router.get("/download-doc/{document_id}/",include_in_schema=False)
def download_document(
        document_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    doc = db.query(Document).filter_by(id=document_id).first()
    if not doc or not doc.raw_pdf:
        raise HTTPException(status_code=404, detail="Document or PDF file not found")

    # Check organization access
    if doc.customer.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")

    file_like = io.BytesIO(doc.raw_pdf)
    headers = {
        "Content-Disposition": f"attachment; filename={doc.filename or 'document.pdf'}"
    }
    return StreamingResponse(file_like, media_type="application/pdf", headers=headers)


@router.get("/get-extracted-data/{document_id}/",include_in_schema=False)
def preview_extracted_data(
        document_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    doc = db.query(Document).filter_by(id=document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Check organization access
    if doc.customer.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")

    if not doc.extracted_data:
        return {"message": "No extracted data available for this document"}

    return {"document_id": doc.id, "extracted_data": doc.extracted_data}


@router.get("/convert-to-excel/{document_id}/",include_in_schema=False)
def extracted_data_to_excel(
        document_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    doc = db.query(Document).filter_by(id=document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Check organization access
    if doc.customer.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")

    extracted_data = doc.extracted_data
    if isinstance(extracted_data, str):
        try:
            extracted_data = json.loads(extracted_data)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Extracted data is not valid JSON")

    if not isinstance(extracted_data, list):
        raise HTTPException(status_code=400, detail="Extracted data should be a list")

    # Group data by page number
    data_by_page = {}
    for item in extracted_data:
        if not isinstance(item, dict):
            continue
        page = item.get("page")
        key = item.get("key")
        value = item.get("value")

        if page is None or key is None:
            continue

        if page not in data_by_page:
            data_by_page[page] = {}
        data_by_page[page][key] = value

    # Create DataFrame and export to Excel
    df = pd.DataFrame.from_dict(data_by_page, orient='index')
    df.index.name = "page"
    df.reset_index(inplace=True)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='ExtractedData')

    output.seek(0)
    return StreamingResponse(
        output,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': f'attachment; filename="document_{document_id}_extracted_data.xlsx"'}
    )


@router.post("/download-excel/",include_in_schema=False)
async def download_excel(data: dict = Body(...)):
    key_value_pairs = data.get("key_value_pairs", [])

    if not key_value_pairs:
        raise HTTPException(status_code=404, detail="No key-value pairs provided")

    df = pd.DataFrame(key_value_pairs)

    # Pivot data so each page is one row and keys are columns
    pivot_df = df.pivot(index="page", columns="key", values="value").reset_index()

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        pivot_df.to_excel(writer, index=False, sheet_name='KeyValueData')

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=extracted_kv.xlsx"}
    )
