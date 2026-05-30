from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from threadcore.infrastructure.db.session import Base, engine


class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    threads = relationship("ThreadDB", back_populates="user")


class ThreadDB(Base):
    __tablename__ = "threads"

    thread_id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False, default="New Chat")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("UserDB", back_populates="threads")

def init_db() -> None:
    Base.metadata.create_all(bind=engine)
