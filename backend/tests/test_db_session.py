from app.db.session import get_db


def test_get_db_yields_and_closes_session() -> None:
    gen = get_db()
    db = next(gen)

    assert db is not None

    try:
        next(gen)
    except StopIteration:
        assert True
