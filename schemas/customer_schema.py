from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, validator


class CustomerCreate(BaseModel):
    name: str
    email:Optional[EmailStr] = None
    # address:Optional[str] = None

    # pages_per_valve: int

class CustomerRead(BaseModel):
    id: int
    name: str
    email :Optional[str]
#     organization_id: int
#     address : str
#     created_at : datetime
#     created_by : str
#     modified_at:datetime
#     modified_by:str
    is_active:bool
    # pages_per_valve: int
    @validator("is_active", pre=True)     #Decorator function run first
    def cast_bool(cls, v):        #cls : Customerrecord
        return bool(v)            #v = raw value from input / DB (true == True)

    model_config = {
        "from_attributes": True
    }
