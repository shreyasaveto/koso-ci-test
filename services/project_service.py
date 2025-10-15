from fastapi import HTTPException,status
from sqlalchemy import func
from models.models import Country, Project, Customer, User
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from schemas.project_schema import ProjectCreate

def all_projects(db, customer_id):
    try:
        projects = db.query(Project.id,Project.name).filter(Project.customer_id == customer_id).all()
        if not projects:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No projects found for this customer"
            )
        return projects
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch projects from the database"
        )

#change country to country id
def create_new_project(req: ProjectCreate, db: Session, current_user: User):
    existing = (
        db.query(Project)
        .filter_by(name=req.name, customer_id= req.customer_id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Project '{req.name}' already exists for this customer.")
    

    # country_exists = (
    #     db.query(Country)
    #     .filter(func.lower(Country.name) == req.country.lower())
    #     .first()
    # )
    country_exists = (
        db.query(Country)
        .filter(Country.id == req.country_id)
        .first()
    )
    if not country_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Country '{req.country_id}' is not in the allowed countries list."
        )
    
    new_project = Project(
        name=req.name,
        country_id=req.country_id,
        customer_id=req.customer_id,
        modified_by=current_user.id,
        created_by=current_user.id,
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return {
        "message": "Project created successfully"
    }

