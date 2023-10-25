from basic_session import create_sessionmaker_from_envs
from sqlalchemy.orm import sessionmaker


def test_should_generate_different_sessions_from_factory():
    factory: sessionmaker = create_sessionmaker_from_envs(pool_size=5)

    sessions=[]

    for x in range(5):
        session = factory()
        sessions.append(session)
        session.execute("select 1")
    
    sessions_set = set(sessions)

    assert len(sessions_set) == len(sessions)

def test_should_use_only_5_connections_between_sessions_when_sessions_are_closed_after_reaching_pool_size():
    factory: sessionmaker = create_sessionmaker_from_envs(pool_size=5, max_overflow=0, pool_timeout=5)

    connections=[]
    sessions = []

    for x in range(15):
        if x%5 == 0 :
            [x.close() for x in sessions]
        session = factory()
        connections.append(session.connection()._dbapi_connection.connection)
        session.execute("select 1")
        sessions.append(session)
    
    connections_set = set(connections)

    assert len(connections) == 15
    assert len(connections_set) == 5

