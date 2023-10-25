from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Factory
import pytest

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
            sessions.append(session)


def test_container_should_raise_timeouteerror_after_reaching_max_overflow():
    # Arrange
    sessions = []

    # Act
    with pytest.raises(expected_exception=TimeoutError):
        for _ in range(5 + 1):
            session = container.db_session()
            sessions.append(session)
