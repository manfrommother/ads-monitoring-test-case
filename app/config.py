from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv


load_dotenv()

class Settings(BaseSettings):
    """
    Класс настроек приложения
    """
    # Параметры базы данных
    DB_USER: str = os.getenv('DB_USER', 'user')
    DB_PASSWORD: str = os.getenv('DB_PASSWORD', 'password')
    DB_HOST: str = os.getenv('DB_HOST', 'localhost')
    DB_NAME: str = os.getenv('DB_NAME', 'avito_parser')
    
    DATABASE_URL: str = os.getenv(
        'DATABASE_URL', 
        f'postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
    )
    
    APP_HOST: str = os.getenv('APP_HOST', '0.0.0.0')
    APP_PORT: int = int(os.getenv('APP_PORT', 8000))
    

    class Config:

        env_file = '.env'
        env_file_encoding = 'utf-8'

# Создаем синглтон настроек
settings = Settings()