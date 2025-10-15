from fastapi import APIRouter, Depends, HTTPException, Request, Response ,status
from sqlalchemy.orm import Session
from auth.security import verify_password
from auth.token import create_access_token
from db.database import get_db
from models.models import User
from schemas.auth_schemas import LoginRequest
from schemas.userSignup_schema import UserResponse, UserCreate
from services.user_services import refresh_access_token, user_login, register_user

# from pydantic import BaseModel


# class LoginRequest(BaseModel):
#     username: str
#     password: str

router = APIRouter()


# @router.post("/login")
# def login(request: LoginRequest, db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.username == request.username).first()
#     if not user or not verify_password(request.password, user.password):
#         raise HTTPException(status_code=401, detail="Invalid credentials")

#     token = create_access_token(data={"sub": str(user.id)})
#     return {"access_token": token, "token_type": "bearer"}

#User Signup logic
@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def register(request: UserCreate, db: Session = Depends(get_db)):
    return await register_user( request , db)

@router.post("/login")
async def login(response: Response, request: LoginRequest, db: Session = Depends(get_db)):
    return await user_login(response, request,db)


@router.post("/refresh")
async def refresh_token(request: Request, db: Session = Depends(get_db)):
    return await refresh_access_token(request,db)