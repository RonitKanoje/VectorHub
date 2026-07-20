import asyncio
import sys
import psycopg
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import declarative_base, sessionmaker
from ai.core.config import settings
from psycopg_pool import AsyncConnectionPool


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

engine = create_engine(settings.database_url) ## connects Python with PostgreSQL
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) ## changing after db.commit()
Base = declarative_base()  ## base class of all ORM


def _psycopg_conninfo() -> str:
    url = make_url(settings.database_url)
    if url.get_backend_name() in {"postgresql", "postgres"}:
        return url.set(drivername="postgresql").render_as_string(hide_password=False)
    return settings.database_url


def get_db():
    db = SessionLocal()   ## creating session
    try:
        yield db ## passes session to the route
    finally:
        db.close()


def get_db_connection(autocommit: bool = True):
    return psycopg.connect(
        _psycopg_conninfo(),
        autocommit=autocommit,
    )

# Pool handling 
def get_async_db_pool():
    return AsyncConnectionPool(
        conninfo=_psycopg_conninfo(),
        kwargs={"autocommit": True},
    )
