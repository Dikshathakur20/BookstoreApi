from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_KEY: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    PROJECT_NAME: str = "Book Store API"
    VERSION: str = "1.0.0"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()