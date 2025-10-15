from enum import Enum
from jose import jwt, JWTError, ExpiredSignatureError
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from core.config import REFRESH_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from models.models import User
from db.database import get_db

security = HTTPBearer()

class TokenType(str, Enum):
    ACCESS = "access_token"
    REFRESH = "refresh_token"

async def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "token_type": TokenType.ACCESS})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def create_refresh_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "token_type": TokenType.REFRESH})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(credentials = Depends(security), db: Session = Depends(get_db)) -> User:
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        token_type: str | None = payload.get("token_type")

        if user_id is None or token_type is None:
            raise HTTPException(status_code=401, detail="Invalid token payload: subject missing")
        if token_type != TokenType.ACCESS:
            raise HTTPException(status_code=401, detail="Invalid token")
        try:
            user_id = int(user_id)
        except (TypeError, ValueError):
            raise HTTPException(status_code=401, detail="Invalid token payload: user id malformed")

        user = db.get(User, user_id) if hasattr(db, "get") else db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def verify_refresh_token(token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str | None = payload.get("sub")
        token_type: str | None = payload.get("token_type")
        if user_id is None or token_type is None:
            raise HTTPException(status_code=401, detail="Invalid token payload: subject missing")
        if token_type != TokenType.REFRESH:
            raise HTTPException(status_code=401, detail="Invalid token")
        try:
            user_id = int(user_id)
        except (TypeError, ValueError):
            raise HTTPException(status_code=401, detail="Invalid token payload: user id malformed")

        user = db.get(User, user_id) if hasattr(db, "get") else db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")