from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    POSTGRES_USER: str = "app_user"
    POSTGRES_PASSWORD: str = "secure_password_here"
    POSTGRES_DB: str = "restaurant_db"
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432
    REDIS_URL: str = "redis://redis:6379/0"

    class Config:
        extra = "ignore"

settings = Settings()