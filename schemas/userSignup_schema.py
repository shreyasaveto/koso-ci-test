from pydantic import BaseModel, EmailStr , constr


class UserCreate(BaseModel):
    username: EmailStr
    password: constr(min_length=6)
    organization_id:int = 1


class UserResponse(BaseModel):
    id:int
    username:str
    organization_id:int

    model_config = {
        "from_attributes": True
    }

