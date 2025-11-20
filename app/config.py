from pydantic import BaseSettings, AnyUrl


class Settings(BaseSettings):
    DATABASE_URL: AnyUrl = "postgresql://postgres:postgres@localhost:5432/products_db"
    REDIS_URL: AnyUrl = "redis://localhost:6379/0"
    SECRET_KEY: str = "changeme"
    ENV: str = "local"

    class Config:
        env_file = ".env"


settings = Settings()
