"""Crawler configuration: load from config file (YAML), support env override."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

BASE_URL_ID = "https://steamcommunity.com/id/{user_id}/reviews"
BASE_URL_PROFILE = "https://steamcommunity.com/profiles/{user_id}/reviews"

USER_AGENT: str = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# Defaults when not in config file (used by load_config and by http_client before apply_config).
DEFAULT_REQUEST_INTERVAL = 2.0
DEFAULT_REQUEST_TIMEOUT = 15
DEFAULT_REQUEST_RETRIES = 3
DEFAULT_OUTPUT_DIR = "data/reviews"
DEFAULT_MAX_PAGES = 500

# Module-level runtime values (set by apply_config, read by http_client).
REQUEST_INTERVAL: float = DEFAULT_REQUEST_INTERVAL
REQUEST_TIMEOUT: int = DEFAULT_REQUEST_TIMEOUT
REQUEST_RETRIES: int = DEFAULT_REQUEST_RETRIES


@dataclass
class CrawlerConfig:
    """Loaded crawler configuration."""

    user_id: str
    use_vanity: bool
    output_dir: Path
    max_pages: int
    request_interval: float
    request_timeout: int
    request_retries: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CrawlerConfig":
        raw_dir = data.get("output_dir", DEFAULT_OUTPUT_DIR)
        out = Path(raw_dir) if isinstance(raw_dir, str) else Path(str(raw_dir))
        return cls(
            user_id=(data.get("user_id") or "").strip(),
            use_vanity=bool(data.get("use_vanity", True)),
            output_dir=out,
            max_pages=int(data.get("max_pages", DEFAULT_MAX_PAGES)),
            request_interval=float(data.get("request_interval", DEFAULT_REQUEST_INTERVAL)),
            request_timeout=int(data.get("request_timeout", DEFAULT_REQUEST_TIMEOUT)),
            request_retries=int(data.get("request_retries", DEFAULT_REQUEST_RETRIES)),
        )


def _config_path() -> Path:
    """Default config file path: STEAM_CONFIG env or config.yaml in cwd, then project root."""
    path = os.environ.get("STEAM_CONFIG", "").strip()
    if path:
        return Path(path)
    cwd_config = Path.cwd() / "config.yaml"
    if cwd_config.is_file():
        return cwd_config
    project_root = Path(__file__).resolve().parent.parent
    root_config = project_root / "config.yaml"
    return root_config if root_config.is_file() else cwd_config


def load_config(config_path: Path | None = None) -> CrawlerConfig:
    """
    Load configuration from YAML file.
    Path: config_path or STEAM_CONFIG env or cwd/config.yaml.
    output_dir in file can be relative or absolute.
    """
    path = config_path or _config_path()
    if not path.is_file():
        raise FileNotFoundError(f"Config file not found: {path}")

    try:
        import yaml
    except ImportError:
        raise ImportError("PyYAML is required for config file. Install: pip install PyYAML") from None

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return CrawlerConfig.from_dict(data)


def apply_config(cfg: CrawlerConfig) -> None:
    """Set module-level request settings used by http_client."""
    global REQUEST_INTERVAL, REQUEST_TIMEOUT, REQUEST_RETRIES
    REQUEST_INTERVAL = cfg.request_interval
    REQUEST_TIMEOUT = cfg.request_timeout
    REQUEST_RETRIES = cfg.request_retries


def get_recommended_url(user_id: str, use_vanity: bool = True) -> str:
    """
    Build the recommended reviews list URL for a user.
    If user_id is purely numeric (64-bit Steam ID), always use /profiles/ path.
    """
    uid = user_id.strip()
    if uid.isdigit():
        return BASE_URL_PROFILE.format(user_id=uid)
    if use_vanity:
        return BASE_URL_ID.format(user_id=uid)
    return BASE_URL_PROFILE.format(user_id=uid)
