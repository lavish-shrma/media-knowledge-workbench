from tests.conftest import client


def test_register_login_refresh_flow() -> None:
    register = client.post(
        "/api/v1/auth/register",
        json={"email": "bonus@example.com", "password": "test-password-123"},
    )
    assert register.status_code == 200
    assert register.json()["email"] == "bonus@example.com"

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "bonus@example.com", "password": "test-password-123"},
    )
    assert login.status_code == 200
    tokens = login.json()
    assert tokens["access_token"]
    assert tokens["refresh_token"]

    refresh = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert refresh.status_code == 200
    assert refresh.json()["access_token"]


def test_duplicate_registration_is_rejected() -> None:
    first = client.post(
        "/api/v1/auth/register",
        json={"email": "dup@example.com", "password": "test-password-123"},
    )
    assert first.status_code == 200

    duplicate = client.post(
        "/api/v1/auth/register",
        json={"email": "dup@example.com", "password": "test-password-123"},
    )
    assert duplicate.status_code == 400
    assert duplicate.json()["detail"] == "Email already registered"


def test_login_rejects_bad_credentials() -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "unknown@example.com", "password": "wrong"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"
