from typing import List
from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import Session

from auth.token import get_current_user
from db.database import get_db
from models.models import User
from schemas.project_schema import ProjectRead, ProjectCreate
from services.project_service import all_projects, create_new_project


router = APIRouter()


@router.get("/{customer_id}/",response_model=List[ProjectRead])
def get_project_list(customer_id :int, db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    projects = all_projects(db = db, customer_id = customer_id)
    return projects

@router.post("/add/")
def new_project(data: ProjectCreate,
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)
    ):
    #create a new project
    return create_new_project(data,db,current_user)