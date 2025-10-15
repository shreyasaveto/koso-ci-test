# from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, Body
# from sqlalchemy.orm import Session
# from backend.models.models import User, Customer, Document, ExtractionTemplate
# from backend.db.database import get_db
# from backend.auth.token import get_current_user
# from pydantic import BaseModel
# from typing import Optional, List, Dict, Any
# from backend.services.ocr_services import process_ocr, process_kv_extraction
# from datetime import datetime
# from starlette.responses import StreamingResponse
# import io
# import json
# import pandas as pd

# router = APIRouter()
#
# class CustomerCreate(BaseModel):
#     name: str
#     pages_per_valve: int
#
# class CustomerRead(BaseModel):
#     id: int
#     name: str
#     organization_id: int
#     pages_per_valve: int
#
#     model_config = {
#         "from_attributes": True
#     }
#
# class OCRBox(BaseModel):
#     id: str
#     bbox: List[List[int]]
#     text: str
#     conf: float
#
# class BoxMapping(BaseModel):
#     key_box: List[List[float]]
#     value_box: List[List[float]]
#
# class ExtractionTemplateCreate(BaseModel):
#     name: str
#     customer_id: int
#     ocr_boxes: List[OCRBox]
#
# class MappingsUpdate(BaseModel):
#     box_mappings: List[BoxMapping]
#
# class ExtractionTemplateOut(BaseModel):
#     id: int
#     name: str
#     customer_id: int
#     ocr_boxes: List[OCRBox]
#     box_mappings: Optional[List[BoxMapping]] = None
#     created_at: datetime
#
# class ExtractedDataIn(BaseModel):
#     extracted_data: Dict[str, Any]
#
# class ExtractedDataIn(BaseModel):
#     extracted_data: Dict[str, Any]

# @router.post("/ocr-extract/")
# async def ocr_extract(pdf: UploadFile = File(...), current_user: User = Depends(get_current_user)):
#     return await process_ocr(pdf)
#
# @router.post("/apply-kv-on-pdf/")
# async def apply_kv_on_pdf(
#     pdf: UploadFile = File(...),
#     key_value_boxes: str = Form(...),
#     current_user: User = Depends(get_current_user)
# ):
#     return await process_kv_extraction(pdf, key_value_boxes)


# @router.post("/add-customer/")
# def add_customer(
#     data: CustomerCreate,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     existing = (
#         db.query(Customer)
#         .filter_by(name=data.name, organization_id=current_user.organization_id)
#         .first()
#     )
#     if existing:
#         raise HTTPException(status_code=400, detail="Customer with this name already exists in your organization.")
#
#     customer = Customer(
#         name=data.name,
#         organization_id=current_user.organization_id,
#         pages_per_valve=data.pages_per_valve,  # required value
#     )
#     db.add(customer)
#     db.commit()
#     db.refresh(customer)
#     return {"message": "Customer created successfully", "customer_id": customer.id}
#
# @router.get("/customers/", response_model=List[CustomerRead])
# def get_customers(
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
#     ):
#     # Filter by current user's organization only
#     customers = db.query(Customer).filter(Customer.organization_id == current_user.organization_id).all()
#     return customers

# @router.post("/templates/", response_model=ExtractionTemplateOut)
# def create_template(
#     payload: ExtractionTemplateCreate,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     # 🔍 Check if the customer exists and belongs to the same organization
#     customer = db.query(Customer).filter_by(
#         id=payload.customer_id,
#         organization_id=current_user.organization_id
#     ).first()
#
#     if not customer:
#         raise HTTPException(
#             status_code=403,
#             detail="You are not authorized to create a template for this customer.",
#         )
#
#     # ✅ Create the template if customer is valid
#     template = ExtractionTemplate(
#         name=payload.name,
#         customer_id=payload.customer_id,
#         ocr_boxes=[box.model_dump() for box in payload.ocr_boxes],
#         box_mappings=None
#     )
#
#     db.add(template)
#     db.commit()
#     db.refresh(template)
#     return template


# @router.patch("/templates/{template_id}/mappings", response_model=ExtractionTemplateOut)
# def update_mappings(
#     template_id: int,
#     payload: MappingsUpdate,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     # 🔍 Fetch template with related customer
#     template = db.query(ExtractionTemplate).filter_by(id=template_id).first()
#     if not template:
#         raise HTTPException(status_code=404, detail="Template not found")
#
#     # 🔐 Permission check: ensure the template belongs to a customer in the user's organization
#     if template.customer.organization_id != current_user.organization_id:
#         raise HTTPException(
#             status_code=403,
#             detail="You are not authorized to update this template.",
#         )
#
#     # ✅ Update mappings
#     template.box_mappings = [mapping.model_dump() for mapping in payload.box_mappings]
#     db.commit()
#     db.refresh(template)
#     return template

# def ensure_user_has_access_to_template(template: ExtractionTemplate, user: User):
#     if template.customer.organization_id != user.organization_id:
#         raise HTTPException(status_code=403, detail="Access denied to this template.")

# @router.get("/templates/{template_id}", response_model=ExtractionTemplateOut)
# def get_template(template_id: int,
#                  db: Session = Depends(get_db),
#                  current_user: User = Depends(get_current_user)):
#     template = db.query(ExtractionTemplate).filter_by(id=template_id).first()
#     if not template:
#         raise HTTPException(status_code=404, detail="Template not found")
#
#     ensure_user_has_access_to_template(template, current_user)
#     return template


# @router.post("/save-doc/")
# async def upload_document(
#     pdf: UploadFile = File(...),
#     customer_id: int = Form(...),
#     template_id: int | None = Form(None),
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),  # Add user dependency
# ):
#     # Validate PDF file type
#     if pdf.content_type != "application/pdf":
#         raise HTTPException(status_code=400, detail="Only PDF files are allowed")
#
#     # Check if customer exists and belongs to current user's organization
#     customer = db.query(Customer).filter_by(
#         id=customer_id,
#         organization_id=current_user.organization_id
#     ).first()
#     if not customer:
#         raise HTTPException(status_code=403, detail="You are not authorized to upload documents for this customer.")
#
#     # If template_id provided, check if template exists and belongs to the same customer
#     if template_id is not None:
#         template = db.query(ExtractionTemplate).filter_by(
#             id=template_id,
#             customer_id=customer_id
#         ).first()
#         if not template:
#             raise HTTPException(status_code=400, detail="Invalid template_id for this customer.")
#
#     pdf_bytes = await pdf.read()
#
#     doc = Document(
#         customer_id=customer_id,
#         uploaded_by_user_id=current_user.id,  # Use current user as uploader
#         filename=pdf.filename,
#         raw_pdf=pdf_bytes,
#         template_id=template_id,
#         uploaded_at=datetime.utcnow(),
#     )
#
#     db.add(doc)
#     db.commit()
#     db.refresh(doc)
#
#     return {
#         "document_id": doc.id,
#         "message": "PDF uploaded successfully",
#         "filename": doc.filename
#     }


# @router.patch("/save-extracted-data/{document_id}/")
# def save_extracted_data(
#     document_id: int,
#     payload: ExtractedDataIn,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),  # Add user dependency
# ):
#     doc = db.query(Document).filter_by(id=document_id).first()
#     if not doc:
#         raise HTTPException(status_code=404, detail="Document not found")
#
#     # Check if document's customer belongs to current user's organization
#     if doc.customer.organization_id != current_user.organization_id:
#         raise HTTPException(status_code=403, detail="You are not authorized to modify this document.")
#
#     doc.extracted_data = payload.extracted_data
#     db.commit()
#     db.refresh(doc)
#
#     return {
#         "message": "Extracted data saved successfully",
#         "document_id": doc.id
#     }


# @router.get("/documents/{document_id}/")
# def get_document(
#     document_id: int,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     doc = db.query(Document).filter_by(id=document_id).first()
#     if not doc:
#         raise HTTPException(status_code=404, detail="Document not found")
#
#     # Check organization access
#     if doc.customer.organization_id != current_user.organization_id:
#         raise HTTPException(status_code=403, detail="Access denied")
#
#     return {
#         "id": doc.id,
#         "filename": doc.filename,
#         "uploaded_at": doc.uploaded_at.isoformat(),
#         "template_id": doc.template_id,
#         "extracted_data": doc.extracted_data,
#         "customer_id": doc.customer_id,
#         "uploaded_by_user_id": doc.uploaded_by_user_id,
#     }
#

# @router.get("/download-doc/{document_id}/")
# def download_document(
#     document_id: int,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     doc = db.query(Document).filter_by(id=document_id).first()
#     if not doc or not doc.raw_pdf:
#         raise HTTPException(status_code=404, detail="Document or PDF file not found")
#
#     # Check organization access
#     if doc.customer.organization_id != current_user.organization_id:
#         raise HTTPException(status_code=403, detail="Access denied")
#
#     file_like = io.BytesIO(doc.raw_pdf)
#     headers = {
#         "Content-Disposition": f"attachment; filename={doc.filename or 'document.pdf'}"
#     }
#     return StreamingResponse(file_like, media_type="application/pdf", headers=headers)


# @router.get("/get-extracted-data/{document_id}/")
# def preview_extracted_data(
#     document_id: int,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     doc = db.query(Document).filter_by(id=document_id).first()
#     if not doc:
#         raise HTTPException(status_code=404, detail="Document not found")
#
#     # Check organization access
#     if doc.customer.organization_id != current_user.organization_id:
#         raise HTTPException(status_code=403, detail="Access denied")
#
#     if not doc.extracted_data:
#         return {"message": "No extracted data available for this document"}
#
#     return {"document_id": doc.id, "extracted_data": doc.extracted_data}


# @router.get("/convert-to-excel/{document_id}/")
# def extracted_data_to_excel(
#     document_id: int,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     doc = db.query(Document).filter_by(id=document_id).first()
#     if not doc:
#         raise HTTPException(status_code=404, detail="Document not found")
#
#     # Check organization access
#     if doc.customer.organization_id != current_user.organization_id:
#         raise HTTPException(status_code=403, detail="Access denied")
#
#     extracted_data = doc.extracted_data
#     if isinstance(extracted_data, str):
#         try:
#             extracted_data = json.loads(extracted_data)
#         except json.JSONDecodeError:
#             raise HTTPException(status_code=400, detail="Extracted data is not valid JSON")
#
#     if not isinstance(extracted_data, list):
#         raise HTTPException(status_code=400, detail="Extracted data should be a list")
#
#     # Group data by page number
#     data_by_page = {}
#     for item in extracted_data:
#         if not isinstance(item, dict):
#             continue
#         page = item.get("page")
#         key = item.get("key")
#         value = item.get("value")
#
#         if page is None or key is None:
#             continue
#
#         if page not in data_by_page:
#             data_by_page[page] = {}
#         data_by_page[page][key] = value
#
#     # Create DataFrame and export to Excel
#     df = pd.DataFrame.from_dict(data_by_page, orient='index')
#     df.index.name = "page"
#     df.reset_index(inplace=True)
#
#     output = io.BytesIO()
#     with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
#         df.to_excel(writer, index=False, sheet_name='ExtractedData')
#
#     output.seek(0)
#     return StreamingResponse(
#         output,
#         media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
#         headers={'Content-Disposition': f'attachment; filename="document_{document_id}_extracted_data.xlsx"'}
#     )

# @router.post("/download-excel/")
# async def download_excel(data: dict = Body(...)):
#     key_value_pairs = data.get("key_value_pairs", [])
#
#     if not key_value_pairs:
#         raise HTTPException(status_code=404, detail="No key-value pairs provided")
#
#     df = pd.DataFrame(key_value_pairs)
#
#     # Pivot data so each page is one row and keys are columns
#     pivot_df = df.pivot(index="page", columns="key", values="value").reset_index()
#
#     output = io.BytesIO()
#     with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
#         pivot_df.to_excel(writer, index=False, sheet_name='KeyValueData')
#
#     output.seek(0)
#     return StreamingResponse(
#         output,
#         media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#         headers={"Content-Disposition": "attachment; filename=extracted_kv.xlsx"}
#     )
