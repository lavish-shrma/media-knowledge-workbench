import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

BASE_DIR = Path(__file__).resolve().parent
TMP_DIR = BASE_DIR / "tmp"
TMP_DIR.mkdir(parents=True, exist_ok=True)

os.environ["DATABASE_URL"] = f"sqlite:///{(TMP_DIR / 'test.db').as_posix()}"
os.environ["UPLOADS_DIR"] = str(TMP_DIR / "uploads")

from app.main import app
from app.db.base import Base
from app.db.session import engine
from app.db.session import SessionLocal
from app.models.user import User
from app.services.auth import create_access_token
from app.services.redis_store import reset_store

Base.metadata.create_all(bind=engine)


def _seed_test_user() -> None:
	with SessionLocal() as db:
		existing = db.query(User).filter(User.email == "tester@example.com").first()
		if existing is None:
			user = User(email="tester@example.com", password_hash="seed")
			db.add(user)
			db.commit()


_seed_test_user()

client = TestClient(app, headers={"Authorization": f"Bearer {create_access_token('tester@example.com')}"})


@pytest.fixture(autouse=True)
def reset_database() -> None:
	Base.metadata.drop_all(bind=engine)
	Base.metadata.create_all(bind=engine)
	_seed_test_user()
	reset_store()
