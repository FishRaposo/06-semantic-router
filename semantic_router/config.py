"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env files."""

    database_url: str = "postgresql+asyncpg://semantic_router:devpassword@localhost:5432/semantic_router"
    embedding_provider: str = "openai"
    openai_api_key: str = ""
    openai_chat_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    sentence_transformers_model: str = "all-MiniLM-L6-v2"
    routes_config: str = "config/routes.yaml"
    policy_config: str = "config/policy.yaml"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "info"
    default_confidence_threshold: float = 0.7
    min_confidence_threshold: float = 0.3

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
