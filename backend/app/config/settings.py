"""
Central configuration for IncidentZero AI backend.
All values are overridable via environment variables / .env file.
"""
import os
from functools import lru_cache

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class Settings:
    # --- App ---
    APP_NAME: str = "IncidentZero AI"
    APP_VERSION: str = "1.0.0"
    ENV: str = os.getenv("ENV", "development")
    DEMO_MODE: bool = os.getenv("DEMO_MODE", "true").lower() == "true"

    # --- Security ---
    SECRET_KEY: str = os.getenv("SECRET_KEY", "incidentzero-dev-secret-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))

    # --- Database ---
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./incidentzero.db")

    # --- CORS ---
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")

    # --- Elasticsearch ---
    ELASTIC_ENABLED: bool = os.getenv("ELASTIC_ENABLED", "false").lower() == "true"
    ELASTIC_URL: str = os.getenv("ELASTIC_URL", "http://localhost:9200")
    ELASTIC_USERNAME: str = os.getenv("ELASTIC_USERNAME", "elastic")
    ELASTIC_PASSWORD: str = os.getenv("ELASTIC_PASSWORD", "changeme")
    ELASTIC_INDEX_PREFIX: str = os.getenv("ELASTIC_INDEX_PREFIX", "incidentzero")

    # --- Gemma / Ollama (local LLM reasoning engine) ---
    GEMMA_ENABLED: bool = os.getenv("GEMMA_ENABLED", "false").lower() == "true"
    OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://localhost:11434")
    GEMMA_MODEL: str = os.getenv("GEMMA_MODEL", "gemma2:9b")
    GEMMA_TEMPERATURE: float = float(os.getenv("GEMMA_TEMPERATURE", "0.2"))
    GEMMA_TIMEOUT_SECONDS: int = int(os.getenv("GEMMA_TIMEOUT_SECONDS", "60"))

    # --- MCP ---
    MCP_SERVER_HOST: str = os.getenv("MCP_SERVER_HOST", "127.0.0.1")
    MCP_SERVER_PORT: int = int(os.getenv("MCP_SERVER_PORT", "8765"))

    # --- Dataset paths (local fallback data engine, used when ELASTIC_ENABLED=false) ---
    DATASET_DIR: str = os.getenv(
        "DATASET_DIR",
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "datasets"),
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
