import psycopg
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from threadcore.core.config import settings
from psycopg_pool import AsyncConnectionPool


engine = create_engine(settings.database_url) ## connects Python with PostgreSQL
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) ## changing after db.commit()
Base = declarative_base()  ## base class of all ORM


def get_db():
    db = SessionLocal()   ## creating session
    try:
        yield db ## passes session to the route
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

# Pool handling 
def get_async_db_pool():
    return AsyncConnectionPool(
        conninfo=f"host=localhost port=5432 dbname={settings.db_name} user={settings.db_user} password={settings.db_password}",
        kwargs={"autocommit": True},
    )

