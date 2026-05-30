import psycopg
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from threadcore.core.config import settings


engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_connection(autocommit: bool = True):
    return psycopg.connect(
        host="localhost",
        port=5432,
        dbname=settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
        autocommit=autocommit,
    )

