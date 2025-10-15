from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Body,status
from sqlalchemy.orm import Session
from auth.token import get_current_user
from models.models import User, Customer, Document, ExtractionTemplate
from services.ocr_services import process_ocr
import fitz

async def create_document(
    pdf: UploadFile,
    customer_id: int,
    template_name: str,
    project_id: int,
    format_id: int,
    fluid_state_id: int,
    page_per_item: int,
    db: Session,
    current_user: User = Depends(get_current_user)
):
    # Validate PDF file type
    if pdf.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Check if customer exists and belongs to current user's organization
    customer = db.query(Customer).filter_by(
        id=customer_id,
        organization_id=current_user.organization_id
    ).first()
    if not customer:
        raise HTTPException(status_code=403, detail="You are not authorized to upload documents for this customer.")

    #get pdf
    pdf_bytes = await pdf.read()
    pdf_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    num_pages = pdf_doc.page_count
    if not (0 < page_per_item <= num_pages):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid 'page_per_item': must be between 1 and {num_pages}"
        )
    # apply ocr get result
    try:
        ocr_output = await process_ocr(pdf_bytes= pdf_bytes, pages = page_per_item)
        ocr_data = ocr_output.get("ocr_results")
        if not ocr_data:
            raise HTTPException(status_code=400, detail="No OCR results found in PDF")
        # save to template table, get id
        template = ExtractionTemplate(
            name=template_name,
            customer_id=customer_id,
            ocr_boxes=ocr_data,  # store OCR boxes here
            box_mappings={},  # you can fill this later if needed
            created_by=current_user.id,
            modified_by=current_user.id,
            created_at=datetime.utcnow(),
            modified_at=datetime.utcnow(),
        )
        db.add(template)
        db.commit()
        db.refresh(template)  
    except Exception as e:
        print(f"Error saving OCR to template: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save OCR results to template"
        )
        
    #save proposal to document table along with template id
    doc = Document(
        customer_id=customer_id,
        created_by=current_user.id,  # Use current user as uploader
        filename=pdf.filename,
        project_id = project_id,
        fluid_state_id = fluid_state_id,
        format_id = format_id,
        page_per_item = page_per_item,
        raw_pdf=pdf_bytes,
        template_id=template.id,
        modified_by= current_user.id,
        modified_at=datetime.utcnow(),
        created_at=datetime.utcnow(),
    )

    db.add(doc)
    db.commit()
    db.refresh(doc)

    return {
        "document_id": doc.id,
        "message": "PDF uploaded successfully",
        "filename": doc.filename,
        "images" : ocr_output["image_base64"],
        "ocr_results" : ocr_output["ocr_results"],
    }