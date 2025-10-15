from pydantic import BaseModel

class CountryRead(BaseModel):
    id: int
    name: str

class FluidStateRead(BaseModel):
    id: int
    fluid_state: str

class FormatRead(BaseModel):
    id: int
    format: str


#Schema for the sizing tool

class SizingToolResponse(BaseModel):
    id:int
    param: str  #Any

    class Config:
        from_attributes = True

