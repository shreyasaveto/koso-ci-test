from fastapi import HTTPException,status
from models.models import Country, Fluid_state, Format
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models.models import Sizingtool


def get_countries(db):
    try:
        countries = db.query(Country.id, Country.name).all()
        return countries
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch countries from the database"
        )

def get_fluid_states(db):
    try:
        fluidStates = db.query(Fluid_state.id, Fluid_state.fluid_state).all()
        return fluidStates
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch fluid states from the database"
        )
    
def get_formats(db):
    try:
        formats = db.query(Format.id, Format.format).all()
        return formats
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch formats from the database"
        )
    
def get_standard_data(fluid_state_id : int, format_id : int , db : Session):
    result = db.query(Sizingtool).filter(
        Sizingtool.fluid_state_id == fluid_state_id,
        Sizingtool.format_id == format_id
    ).all()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No matching parameter found for the fluid_state_id = {fluid_state_id}  and for the formate = {format_id}"
        )

    return result