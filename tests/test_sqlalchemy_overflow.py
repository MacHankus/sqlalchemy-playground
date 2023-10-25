from basic_session import create_sessionmaker_from_envs
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import TimeoutError
import pytest



def test_should_raise_overflow_error():
    factory: sessionmaker = create_sessionmaker_from_envs(pool_size=5, pool_timeout=5, max_overflow=0)

    with pytest.raises(expected_exception=TimeoutError):
        sessions=[]

        for x in range(6):
            session = factory()
            sessions.append(session)
            session.execute("select :x", params={"x": x})

def test_should_raise_timeouterror_when_overflow_reached():
    factory: sessionmaker = create_sessionmaker_from_envs(pool_size=5, pool_timeout=5, max_overflow=5)

    with pytest.raises(expected_exception=TimeoutError):
        sessions=[]

        for x in range(11):
            session = factory()
            sessions.append(session)
            session.execute("select :x", params={"x": x})

def test_should_not_raise_timeouterror_when_session_is_closed_after_query():
    factory: sessionmaker = create_sessionmaker_from_envs(pool_size=5, pool_timeout=5, max_overflow=5)

    sessions=[]

    for x in range(30):
        session = factory()
        sessions.append(session)
        with session as s:
            s.execute("select :x", params={"x": x})
