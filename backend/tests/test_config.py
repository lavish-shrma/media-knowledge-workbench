from app.core.config import get_settings


def test_settings_defaults_are_loaded() -> None:
    settings = get_settings()

    assert settings.app_name
    assert settings.api_v1_prefix == "/api/v1"
    assert "://" in settings.database_url
