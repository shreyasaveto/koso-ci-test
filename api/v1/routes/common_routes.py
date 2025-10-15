from typing import List

from fastapi import APIRouter, status
from fastapi.params import Depends, Query
from sqlalchemy.orm import Session

from auth.token import get_current_user
from db.database import get_db
from models.models import User
from schemas.common_schemas import CountryRead, FluidStateRead, FormatRead, SizingToolResponse
from services.common_services import get_countries, get_fluid_states, get_formats, get_standard_data

router = APIRouter()


@router.get("/countries/", response_model=List[CountryRead])
def get_countries_list(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    countries = get_countries(db)
    return countries


@router.get("/fluid-states/", response_model=List[FluidStateRead])
def get_fluidState_list(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    fluid_states = get_fluid_states(db)
    return fluid_states


@router.get("/formats/", response_model=List[FormatRead])
def get_format_list(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    formats = get_formats(db)
    return formats


# for the sizing tool seed data

@router.get("/standard-params/", status_code=status.HTTP_200_OK, response_model=List[SizingToolResponse])
def get_standard_params(
        fluid_state_id: int = Query(..., gt=0, description="Fluid state ID must be a positive integer"),
        format_id: int = Query(..., gt=0, description="Fluid state ID must be a positive integer"),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)

):
    return get_standard_data(fluid_state_id, format_id, db)
