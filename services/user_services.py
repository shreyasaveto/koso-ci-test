from fastapi import HTTPException, Request, Response, status
from fastapi.params import Depends
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from auth.security import hash_password, verify_password
from auth.token import create_access_token, create_refresh_token, verify_refresh_token
from models.models import Organization, User
from schemas.auth_schemas import LoginRequest
from schemas.userSignup_schema import UserCreate


async def register_user(request: UserCreate , db: Session):
    try:
        # username already exists
        existing_user = db.query(User).filter(User.username == request.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Username already exists: {existing_user.username}"
            )

        # organization exists
        org_exist = db.query(Organization).filter(Organization.id == request.organization_id).first()

        if not org_exist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="organization does not exist"
            )

        new_user = User(
            username=request.username,
            password=hash_password(request.password),
            organization_id=1
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user

    except HTTPException:
        raise

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected server error: {str(e)}"
        )
    
async def user_login(response, request, db):
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not verify_password(request.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = await create_access_token(data={"sub": str(user.id)})
    refresh_token = await create_refresh_token(data={"sub": str(user.id)})
    max_age = 60 * 60 * 60
    response.set_cookie(
        key="refresh_token", value=refresh_token, httponly=True, secure=True, samesite="lax", max_age=max_age
    )
    return {"access_token": access_token}

async def refresh_access_token(request, db):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing.",
        )

    user = await verify_refresh_token(refresh_token, db=db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token.",
        )

    new_access_token = await create_access_token(data={"sub": str(user.id)})
    new_refresh_token = await create_refresh_token(data={"sub": str(user.id)})

    response = JSONResponse(
        content={"access_token": new_access_token}
    )
    response.delete_cookie(key="refresh_token", path="/")
    max_age = 60 * 60 * 60
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        path="/",
        samesite="lax",
        secure=True,
        max_age= max_age,
    )

    return response

