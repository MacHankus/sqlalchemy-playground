from typing import Any
from sqlalchemy.orm import Session, create_session, scoped_session, sessionmaker
from sqlalchemy import create_engine
from settings import settings


def create_url(
    host: str, port: int, username: str, password: str, db_name: str, driver: str
) -> str:
    url = (
        f"mssql+pyodbc://{username}:{password}@{host}:{port}/{db_name}?driver={driver}"
    )
    return url


def create_single_engine(host: str, port: int, username: str, password: str, db_name: str, driver: str, **kwargs) -> Any:
    url = create_url(
        host, port, username, password, db_name, driver
    )
    return create_engine(url, echo=True, echo_pool=True, logging_name="SQLAlchemy", pool_logging_name="SQLAlchemyPool", **kwargs)


def create_sessionmaker(engine) -> sessionmaker:
    return sessionmaker(bind=engine)

def create_sessionmaker_from_envs(**kwargs) -> sessionmaker:
    engine = create_single_engine(
        settings.DB_HOST,
        settings.DB_PORT,
        settings.DB_USER,
        settings.DB_PASSWORD,
        settings.DB_NAME,
        settings.DB_DRIVER,
        **kwargs
    )
    factory = create_sessionmaker(engine)

    return factory