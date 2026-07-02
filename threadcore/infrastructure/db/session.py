import asyncio
import sys

import psycopg
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from threadcore.core.config import settings


def configure_asyncio_for_windows() -> None:
    if sys.platform != "win32":
        return

    try:
        policy = asyncio.get_event_loop_policy()
        if not isinstance(policy, asyncio.WindowsSelectorEventLoopPolicy):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except AttributeError:
        pass


configure_asyncio_for_windows()

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

