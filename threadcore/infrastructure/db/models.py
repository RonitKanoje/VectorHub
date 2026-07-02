from threadcore.infrastructure.db.session import engine, Base
from threadcore.domains.rag.models import (
    MemoryConflictDB,
    MemoryEventDB,
    MemoryTopicDB,
    MemoryTopicEvidenceDB,
    MemoryTopicVersionDB,
    ThreadDB,
    UserMemoryDB,
)
from threadcore.domains.analyst.models import DatasetDB

# Re-export models for backward compatibility
__all__ = [
    "ThreadDB",
    "UserMemoryDB",
    "MemoryTopicDB",
    "MemoryEventDB",
    "MemoryTopicEvidenceDB",
    "MemoryTopicVersionDB",
    "MemoryConflictDB",
    "DatasetDB",
    "init_db",
]

def init_db() -> None:
    """
    Create all database tables from the current SQLAlchemy models.
    Safe to call on every application startup.
    """
    Base.metadata.create_all(bind=engine) ## creating all registered tables inside base

