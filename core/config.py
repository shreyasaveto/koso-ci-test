import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

DATABASE_URL = "postgresql://dataextractuser:Deaveto123@13.203.125.0:5432/dataextractdb"
SECRET_KEY = "t_lhaqLsIvocE08qu4I-JIr4WGGpOY_ySVakkZQXaA"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_MINUTES = 1440
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")

class Settings(BaseSettings):
    PROJECT_NAME: str = "KOSO"
    BACKEND_CORS_ORIGINS: list[str] = ["*"]
    ENVIRONMENT: str = "dev"


    class Config:
        env_file = ".env"

settings = Settings()
