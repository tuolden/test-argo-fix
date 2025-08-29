"""Unit tests for configuration."""

# Import Settings dynamically based on detected package name under src/
import pathlib
import pkgutil
import sys

src_dir = pathlib.Path(__file__).resolve().parents[2] / "src"
sys.path.insert(0, str(src_dir))
project_name = next(
    m.name for m in pkgutil.iter_modules([str(src_dir)]) if not m.name.startswith(".")
)
mod = __import__(f"{project_name}.core.config", fromlist=["Settings", "get_settings"])  # type: ignore
Settings = getattr(mod, "Settings")  # type: ignore
get_settings = getattr(mod, "get_settings")  # type: ignore


def test_settings_creation():
    """Test settings can be created."""
    settings = Settings()

    assert settings.project_name is not None
    assert settings.host == "127.0.0.1"
    assert settings.port == 8080
    assert settings.debug is False
    assert settings.log_level == "INFO"


def test_get_settings():
    """Test get_settings function."""
    settings = get_settings()

    assert isinstance(settings, Settings)
    assert settings.project_name is not None


def test_settings_caching():
    """Test that settings are cached."""
    settings1 = get_settings()
    settings2 = get_settings()

    # Should be the same instance due to lru_cache
    assert settings1 is settings2


def test_settings_defaults():
    """Test default settings values."""
    settings = Settings()

    assert settings.api_v1_str == "/api/v1"
    assert settings.allowed_hosts == ["*"]
