from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Factory
import pytest
from sqlalchemy.exc import TimeoutError

from basic_session import create_sessionmaker_from_envs


class Container(DeclarativeContainer):
    db_session = Factory(
        create_sessionmaker_from_envs(max_overflow=0, pool_size=5, pool_timeout=5)
    )


container = Container()
container.init_resources()


def test_container_should_create_5_different_sessions():
    # Arrange
    sessions = []

    # Act

    for _ in range(5):
        session = container.db_session()
        session.execute('select 1')
        sessions.append(session)

    # Assert

    assert len(sessions) == len(set(sessions))


def test_container_should_not_raise_timeouteerror_when_generating_number_of_sessions_equal_to_pool_size():
    # Arrange
    sessions = []

    # Act
    with pytest.raises(expected_exception=TimeoutError):
        for _ in range(5 + 1):
            session = container.db_session()
            session.execute('select 1')
            sessions.append(session)


def test_container_should_raise_timeouteerror_after_reaching_max_overflow():
    # Arrange
    sessions = []

    # Act
    with pytest.raises(expected_exception=TimeoutError):
        for _ in range(5 + 1):
            session = container.db_session()
            session.execute('select 1')
            sessions.append(session)


def test_container_should_not_raise_timeouteerror_when_sessions_are_closed():
    # Arrange
    sessions = []

    # Act
    for _ in range(30):
        session = container.db_session()
        with session as s:
            s.execute('select 1')
            sessions.append(s)
