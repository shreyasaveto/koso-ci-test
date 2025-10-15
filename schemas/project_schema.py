from pydantic import BaseModel


class ProjectRead(BaseModel):
    id: int
    name: str

class ProjectCreate(BaseModel):
    name: str
    customer_id : int
    country_id : int


