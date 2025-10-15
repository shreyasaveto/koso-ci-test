from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models.models import Document, ExtractionTemplate, User,Customer
from schemas.template_schema import EditTemplateDataIn

def update_template(data: EditTemplateDataIn, db: Session, current_user: User):

    doc = db.query(Document).filter_by(id=data.document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # if doc.customer.organization_id != current_user.organization_id :
    #     raise HTTPException(status_code=403, detail="You are not authorized to modify this document")

    template = db.query(ExtractionTemplate).filter_by(id=doc.template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Associated template not found")

    template.ocr_boxes = data.ocr_boxes
    template.box_mappings = data.box_mappings
    template.modified_by = current_user.id


    db.commit()
    db.refresh(template)

    return {
        "message": "Template updated successfully",
        "template_id": template.id,
    }
