from functools import lru_cache
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    database_url: str = Field(default="", validation_alias="DATABASE_URL")
    db_name: str = Field(default="", validation_alias="DB_NAME")
    db_user: str = Field(default="", validation_alias="DB_USER")
    db_password: str = Field(default="", validation_alias="DB_PASSWORD")
    session_secret_key: str = Field(default="change-me", validation_alias="SESSION_SECRET_KEY")

    langchain_api_key: str | None = Field(default=None, validation_alias="LANGCHAIN_API_KEY")
    langchain_tracing_v2: str | None = Field(default=None, validation_alias="LANGCHAIN_TRACING_V2")
    langchain_endpoint: str | None = Field(default=None, validation_alias="LANGCHAIN_ENDPOINT")
    langchain_project: str | None = Field(default=None, validation_alias="LANGCHAIN_PROJECT")

    groq_api_key: str = Field(default="", validation_alias="GROQ_API_KEY")  # ← added

    qdrant_url: str = Field(default="http://localhost:6333", validation_alias="QDRANT_URL")
    redis_host: str = Field(default="127.0.0.1", validation_alias="REDIS_HOST")
    redis_port: int = Field(default=6379, validation_alias="REDIS_PORT")
    ollama_chat_model: str = Field(default="llama3.2", validation_alias="OLLAMA_CHAT_MODEL")
    ollama_embedding_model: str = Field(default="bge-m3", validation_alias="OLLAMA_EMBEDDING_MODEL")

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