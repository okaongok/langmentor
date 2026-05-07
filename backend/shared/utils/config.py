from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    service_name: str = "langmentor"
    rabbitmq_url: str = "amqp://admin:admin123@localhost:5672/"
    redis_url: str = "redis://localhost:6379/0"
    database_url: str = "mysql+pymysql://langmentor_user:langmentor_pass@localhost:3306/langmentor_db"
    rag_service_url: str = "http://localhost:8081"
    llm_service_url: str = "http://localhost:8082"
    chroma_host: str = "localhost"
    chroma_port: int = 8000
    openai_api_key: str = ""
    celery_broker_url: str = "amqp://admin:admin123@localhost:5672/"
    celery_result_backend: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
