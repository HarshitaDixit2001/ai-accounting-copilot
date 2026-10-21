import os

from dotenv import load_dotenv


load_dotenv()


class Settings:
    APP_NAME: str = os.getenv(
        "APP_NAME",
        "AI Accounting Copilot",
    )

    APP_VERSION: str = os.getenv(
        "APP_VERSION",
        "0.1.0",
    )

    ENVIRONMENT: str = os.getenv(
        "ENVIRONMENT",
        "development",
    )

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./accounting.db",
    )

    OLLAMA_BASE_URL: str = os.getenv(
        "OLLAMA_BASE_URL",
        "http://localhost:11434",
    )

    OLLAMA_MODEL: str = os.getenv(
        "OLLAMA_MODEL",
        "qwen3:8b",
    )

    RAG_SIMILARITY_THRESHOLD: float = float(
        os.getenv(
            "RAG_SIMILARITY_THRESHOLD",
            "0.45",
        )
    )

    EXPOSE_METRICS: bool = os.getenv(
        "EXPOSE_METRICS",
        "true",
    ).lower() == "true"

    MAX_PROMPT_LENGTH: int = int(
        os.getenv(
            "MAX_PROMPT_LENGTH",
            "5000",
        )
    )
    AUDIT_API_KEY: str = os.getenv(
        "AUDIT_API_KEY",
        "",
    )
    AUDIT_RETENTION_DAYS: int = int(
    os.getenv("AUDIT_RETENTION_DAYS", "90")
    )

settings = Settings()