from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from core.logger_config import logger
from models.models import User, Customer
from schemas.customer_schema import CustomerCreate


def create_customer(db: Session, data: CustomerCreate, current_user: User):
    # Check duplicate name (case-insensitive)

    existing = (
        db.query(Customer)
        .filter(
            func.lower(Customer.name) == func.lower(data.name),
            Customer.organization_id == current_user.organization_id
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Customer with this name '{data.name}' already exists in your organization."
        )

    # Check duplicate email (case-insensitive)
    if data.email:
        existing_email = (
            db.query(Customer)
            .filter(
                func.lower(Customer.email) == func.lower(data.email),
                Customer.organization_id == current_user.organization_id
            )
            .first()
        )
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Customer with email '{data.email}' already exists in your organization."
            )

    # Create new customer
    customer = Customer(
        name=data.name,
        email=data.email,
        organization_id=current_user.organization_id,
        modified_by=current_user.id,
        created_by=current_user.id,
    )

    db.add(customer)
    db.commit()
    db.refresh(customer)
    return {"message": "Customer created successfully"}


def get_customer(db: Session, current_user: User):
    # Filter by current user's organization only the active users
    customers = db.query(Customer).filter(
        Customer.organization_id == current_user.organization_id, Customer.is_active == True
    ).all()
    logger.debug(f"Customers data: {customers}")

    return customers
