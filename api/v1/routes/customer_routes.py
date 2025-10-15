from typing import List

from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.orm import Session
from services.customer_service import get_customer, create_customer
from auth.token import get_current_user
from db.database import get_db
from models.models import User, Customer
# from backend.api.v1.routes.routes import CustomerCreate , CustomerRead
from schemas.customer_schema import CustomerCreate, CustomerRead

router = APIRouter()


@router.post("/add/" , status_code=status.HTTP_201_CREATED)
def add_customer(
        data: CustomerCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    # existing = (
    #     db.query(Customer)
    #     .filter_by(name=data.name, organization_id=current_user.organization_id)
    #     .first()
    # )
    # if existing:
    #     raise HTTPException(status_code=400, detail=f"Customer with this name {data.name} already exists in your organization.")
    #
    # customer = Customer(
    #     name=data.name,
    #     email=data.email,
    #     organization_id=current_user.organization_id,
    #     address=data.address,
    #     modified_by=current_user.id,
    #     created_by=current_user.id,
    #     is_active=True
    #
    #     # pages_per_valve=data.pages_per_valve,  # required value
    # )
    # db.add(customer)
    # db.commit()
    # db.refresh(customer)
    # return {
    #     "message": "Customer created successfully"
    # }
    return create_customer(db,data ,current_user)


@router.get("/", response_model=List[CustomerRead])
def get_customers(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    # # Filter by current user's organization only
    # customers = db.query(Customer).filter(Customer.organization_id == current_user.organization_id).all()
    # return customers
    return get_customer(db,current_user)
