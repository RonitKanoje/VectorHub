from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    database_url: str = Field(default="", validation_alias="DATABASE_URL")
    db_name: str = Field(default="", validation_alias="DB_NAME")
    db_user: str = Field(default="", validation_alias="DB_USER")
    db_password: str = Field(default="", validation_alias="DB_PASSWORD")
    session_secret_key: str = Field(
        default="change-me",
        validation_alias="SESSION_SECRET_KEY",
    )

    # LangSmith
    langsmith_api_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices("LANGSMITH_API_KEY"),
    )

    langchain_tracing_v2: str | None = Field(
        default=None,
        validation_alias=AliasChoices("LANGSMITH_TRACING"),
    )

    langsmith_endpoint: str | None = Field(
        default=None,
        validation_alias=AliasChoices("LANGSMITH_ENDPOINT"),
    )

    langsmith_project: str | None = Field(
        default=None,
        validation_alias=AliasChoices("LANGSMITH_PROJECT"),
    )

    # Groq (actual env vars)
    groq_api_key: str = Field(
        default="",
        validation_alias="GROQ_API_KEY",
    )

    groq_model: str = Field(
        default="llama-3.3-70b-versatile",
        validation_alias="GROQ_MODEL",
    )

    # ------------------------------------------------------------------
    # KEEP THESE NAMES.
    # Existing code uses:
    # settings.gemini_api_key
    # settings.gemini_memory_model
    #
    # During development they will read GROQ values instead.
    # ------------------------------------------------------------------

    gemini_api_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "GEMINI_API_KEY",
            "GROQ_API_KEY",
        ),
    )

    gemini_memory_model: str = Field(
        default="llama-3.3-70b-versatile",
        validation_alias=AliasChoices(
            "GEMINI_MEMORY_MODEL",
            "GROQ_MODEL",
        ),
    )

    # Keep embeddings on Gemini
    gemini_embedding_model: str = Field(
        default="gemini-embedding-001",
        validation_alias="GEMINI_EMBEDDING_MODEL",
    )

    # Infrastructure
    qdrant_url: str = Field(
        default="http://localhost:6333",
        validation_alias="QDRANT_URL",
    )

    redis_host: str = Field(
        default="127.0.0.1",
        validation_alias="REDIS_HOST",
    )

    redis_port: int = Field(
        default=6379,
        validation_alias="REDIS_PORT",
    )

    context_summary_threshold: int = Field(
        default=24,
        validation_alias="CONTEXT_SUMMARY_THRESHOLD",
    )

    context_recent_message_limit: int = Field(
        default=10,
        validation_alias="CONTEXT_RECENT_MESSAGE_LIMIT",
    )

    context_summary_min_new_messages: int = Field(
        default=6,
        validation_alias="CONTEXT_SUMMARY_MIN_NEW_MESSAGES",
    )

    context_summary_max_transcript_chars: int = Field(
        default=24000,
        validation_alias="CONTEXT_SUMMARY_MAX_TRANSCRIPT_CHARS",
    )

    context_important_fact_limit: int = Field(
        default=20,
        validation_alias="CONTEXT_IMPORTANT_FACT_LIMIT",
    )

    log_level: str = Field(
        default="DEBUG",
        validation_alias="LOG_LEVEL",
    )

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def data_dir(self) -> Path:
        return BASE_DIR / "data"

    @property
    def runtime_dir(self) -> Path:
        return self.data_dir / "runtime"

    @property
    def uploads_dir(self) -> Path:
        return self.runtime_dir / "uploads"

    @property
    def audio_upload_dir(self) -> Path:
        return self.uploads_dir / "audio"

    @property
    def video_upload_dir(self) -> Path:
        return self.uploads_dir / "video"

    @property
    def samples_dir(self) -> Path:
        return self.data_dir / "samples"

    def ensure_runtime_directories(self) -> None:
        for path in (
            self.data_dir,
            self.runtime_dir,
            self.uploads_dir,
            self.audio_upload_dir,
            self.video_upload_dir,
            self.samples_dir,
        ):
            path.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_runtime_directories()
    return settings


settings = get_settings()
