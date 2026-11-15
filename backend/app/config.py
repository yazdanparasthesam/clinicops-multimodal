from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite:///./clinicops.db"
    jwt_secret: str = "compose-dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_hours: int = 24
    ai_provider: str = "mock"  # mock | gemini
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"
    ai_max_critique_loops: int = 2
    cors_origins: str = "*"
    otel_enabled: bool = False
    otel_environment: str = "dev"
    otel_service_name: str = "clinicops-backend"
    otel_exporter_otlp_endpoint: str = "http://otel-collector:4317"
    storage_backend: str = "local"
    storage_path: str = "./storage_test"
    version: str = "0.2.0"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
