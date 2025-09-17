from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ENV: str = "development"
    MONGO_URI: str = "mongodb+srv://Ayush:86tsDKQcAkwvCV4g@cluster0.cp2ebzm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    MONGO_DB: str = "buybixx"
    JWT_SECRET: str = "change_me"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRES_MIN: int = 60 * 24 * 7   # 7 days
    BCRYPT_ROUNDS: int = 12
    MODEL_REFRESH_CRON: str = "0 3 * * *"
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"

settings = Settings()
