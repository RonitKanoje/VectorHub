from sqlalchemy import Column, DateTime, String, func

from threadcore.infrastructure.db.session import Base, engine


class ThreadDB(Base):
    """Chat thread metadata - user_id references MongoDB user ObjectId"""
    __tablename__ = "threads"

    thread_id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False, default="New Chat")
    user_id = Column(String, nullable=False, index=True)  # MongoDB ObjectId as string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
