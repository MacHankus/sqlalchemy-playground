from basic_session import create_sessionmaker_from_envs
from sqlalchemy.orm import sessionmaker


def test_should_generate_different_sessions_from_factory():
    pool_size = 5
    factory: sessionmaker = create_sessionmaker_from_envs(
        pool_size=pool_size
    )

    sessions = []

    for _ in range(pool_size):
        session = factory()
        sessions.append(session)
        session.execute("select 1")

    sessions_set = set(sessions)

    assert len(sessions_set) == len(sessions)


def test_should_use_only_5_connections_between_sessions_when_sessions_are_closed_after_reaching_pool_size():
    pool_size = 5
    factory: sessionmaker = create_sessionmaker_from_envs(
        pool_size=pool_size, max_overflow=0, pool_timeout=5
    )

    connections = []
    sessions = []

    for x in range(15):
        if x % 5 == 0:
            [x.close() for x in sessions]
        session = factory()
        connections.append(session.connection()._dbapi_connection.connection)
        session.execute("select 1")
        sessions.append(session)

    connections_set = set(connections)

    assert len(connections) == 15
    assert len(connections_set) == 5


def test_session_could_be_used_in_with_block_multiple_times():
    pool_size = 5
    factory: sessionmaker = create_sessionmaker_from_envs(
        pool_size=pool_size, max_overflow=0, pool_timeout=5
    )

    session = factory()

    for _ in range(3):
        with session as s:
            s.execute("select 1")


def test_session_has_same_connection_when_other_connection_is_created():
    # Arrange
    pool_size = 5
    factory: sessionmaker = create_sessionmaker_from_envs(
        pool_size=pool_size, max_overflow=0, pool_timeout=5
    )
    session = factory()

    # Act

    connection = None
    with session as s:
        assert session.connection()._dbapi_connection.dbapi_connection is not None
        connection = session.connection()._dbapi_connection.dbapi_connection
        s.execute("select 1")

    other_session = factory()
    with other_session as o_s:
        with session as s:
            s.execute("select 1")
            assert session.connection()._dbapi_connection.dbapi_connection is connection


def test_session_has_different_connection_comparing_other_session():
    # Arrange
    pool_size = 5
    factory: sessionmaker = create_sessionmaker_from_envs(
        pool_size=pool_size, max_overflow=0, pool_timeout=5
    )
    session = factory()
    other_session = factory()

    # Act

    with other_session as o_s:
        with session as s:
            s.execute("select 1")
            assert (
                session.connection()._dbapi_connection.dbapi_connection
                is not other_session.connection()._dbapi_connection.dbapi_connection
            )


def test_session_has_still_different_connection_even_after_closing_by_with_block():
    # Arrange
    pool_size = 5
    factory: sessionmaker = create_sessionmaker_from_envs(
        pool_size=pool_size, max_overflow=0, pool_timeout=5
    )
    session = factory()
    other_session = factory()

    connection = None
    with session as s:
        assert session.connection()._dbapi_connection.dbapi_connection is not None
        connection = session.connection()._dbapi_connection.dbapi_connection
        s.execute("select 1")

    # Act

    with other_session as o_s:
        with session as s:
            s.execute("select 1")
            assert session.connection()._dbapi_connection.dbapi_connection is connection
            assert (
                session.connection()._dbapi_connection.dbapi_connection
                is not other_session.connection()._dbapi_connection.dbapi_connection
            )


def test_session_has_still_different_connection_even_after_closing_by_close_function():
    # Arrange
    pool_size = 5
    factory: sessionmaker = create_sessionmaker_from_envs(
        pool_size=pool_size, max_overflow=0, pool_timeout=5
    )
    session = factory()
    other_session = factory()

    connection = None
    assert session.connection()._dbapi_connection.dbapi_connection is not None
    connection = session.connection()._dbapi_connection.dbapi_connection
    session.execute("select 1")
    session.close()

    # Act

    with other_session as o_s:
        with session as s:
            s.execute("select 1")
            assert session.connection()._dbapi_connection.dbapi_connection is connection
            assert (
                session.connection()._dbapi_connection.dbapi_connection
                is not other_session.connection()._dbapi_connection.dbapi_connection
            )


def test_session_has_still_same_connection_even_after_other_sessions_making_queue_pool_empty():
    # Arrange
    pool_size = 5
    factory: sessionmaker = create_sessionmaker_from_envs(
        pool_size=pool_size, max_overflow=0, pool_timeout=5
    )
    session = factory()

    connection = None
    assert session.connection()._dbapi_connection.dbapi_connection is not None
    connection = session.connection()._dbapi_connection.dbapi_connection
    session.execute("select 1")
    session.close()

    other_sessions = []

    # Act

    for _ in range(pool_size):
        session = factory()
        session.execute("select 1")
        other_sessions.append(session)

    assert session.connection()._dbapi_connection.dbapi_connection is connection
