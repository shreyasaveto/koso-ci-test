from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from auth.token import get_current_user
from db.database import get_db
from models.models import User, Customer, ExtractionTemplate
# from backend.api.v1.routes.routes import ExtractionTemplateCreate , ExtractionTemplateOut , MappingsUpdate
from schemas.template_schema import EditTemplateDataIn, ExtractionTemplateCreate, ExtractionTemplateOut, MappingsUpdate
from services.template_service import update_template

router = APIRouter()


def ensure_user_has_access_to_template(template: ExtractionTemplate, user: User):
    if template.customer.organization_id != user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied to this template.")


# CREATE Template
@router.post("/templates/", response_model=ExtractionTemplateOut,include_in_schema=False)
def create_template(
        payload: ExtractionTemplateCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    # 🔍 Check if the customer exists and belongs to the same organization
    customer = db.query(Customer).filter_by(
        id=payload.customer_id,
        organization_id=current_user.organization_id
    ).first()

    if not customer:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to create a template for this customer.",
        )

    # ✅ Create the template if customer is valid
    template = ExtractionTemplate(
        name=payload.name,
        customer_id=payload.customer_id,
        ocr_boxes=[box.model_dump() for box in payload.ocr_boxes],
        box_mappings=None
    )

    db.add(template)
    db.commit()
    db.refresh(template)
    return template


# Update template mapping

@router.patch("/templates/{template_id}/mappings", response_model=ExtractionTemplateOut,include_in_schema=False)
def update_mappings(
        template_id: int,
        payload: MappingsUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    # 🔍 Fetch template with related customer
    template = db.query(ExtractionTemplate).filter_by(id=template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # 🔐 Permission check: ensure the template belongs to a customer in the user's organization
    if template.customer.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to update this template.",
        )

    # ✅ Update mappings
    template.box_mappings = [mapping.model_dump() for mapping in payload.box_mappings]
    db.commit()
    db.refresh(template)
    return template


# Get the template based on the id

@router.get("/templates/{template_id}", response_model=ExtractionTemplateOut,include_in_schema=False)
def get_template(template_id: int,
                 db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    template = db.query(ExtractionTemplate).filter_by(id=template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    ensure_user_has_access_to_template(template, current_user)
    return template


@router.patch("/edit/{document_id}/",include_in_schema=True)
def edit_template_data(
    data: EditTemplateDataIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_template(
        data = data,
        db = db,
        current_user = current_user,
    )
