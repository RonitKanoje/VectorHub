from threadcore.infrastructure.db.session import engine, Base
from threadcore.domains.rag.models import ( ## when we import models basically we are executing the model definitions and registering them with SQLAlchemy's metadata(Base). This is necessary for creating tables in the database.
    MemoryConflictDB,
    MemoryEventDB,
    MemoryTopicDB,
    MemoryTopicEvidenceDB,
    MemoryTopicVersionDB,
    ThreadDB,
)
from threadcore.domains.analyst.models import DatasetDB

# Re-export models for backward compatibility
__all__ = [
    "ThreadDB",
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

