from basic_session import create_sessionmaker_from_envs
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import TimeoutError
import pytest


def test_should_raise_timeouterror_error():
    factory: sessionmaker = create_sessionmaker_from_envs(
        pool_size=5, pool_timeout=5, max_overflow=0
    )

    with pytest.raises(expected_exception=TimeoutError):
        sessions = []

        for x in range(6):
            session = factory()
            sessions.append(session)
            session.execute("select :x", params={"x": x})


def test_should_raise_timeouterror_when_overflow_reached():
    factory: sessionmaker = create_sessionmaker_from_envs(
        pool_size=5, pool_timeout=5, max_overflow=5
    )

    with pytest.raises(expected_exception=TimeoutError):
        sessions = []

        for x in range(11):
            session = factory()
            sessions.append(session)
            session.execute("select :x", params={"x": x})


def test_should_not_raise_timeouterror_when_session_is_closed_after_query():
    factory: sessionmaker = create_sessionmaker_from_envs(
        pool_size=5, pool_timeout=5, max_overflow=5
    )

    sessions = []

    for x in range(30):
        session = factory()
        sessions.append(session)
        with session as s:
            s.execute("select :x", params={"x": x})



def test_session_should_raise_timeouterror_when_other_sessions_exhaust_queue_pool():
    # Arrange
    pool_size = 5
    factory: sessionmaker = create_sessionmaker_from_envs(
        pool_size=pool_size, pool_timeout=5, max_overflow=0
    )

    # create and use main session
    main_session = factory()
    with main_session as s:
        s.execute('select 1')

    # create other sessions , exhausting the pool and not closing sessions
    sessions = []

    for x in range(pool_size):
        session = factory()
        sessions.append(session)
        session.execute("select :x", params={"x": x})
    
    # Act
    with pytest.raises(expected_exception=TimeoutError):
        # after exhausting the pool and not releasing connections old session should hang until TimeoutError
        main_session.execute('select 1')

