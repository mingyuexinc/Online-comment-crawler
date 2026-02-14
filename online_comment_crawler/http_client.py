"""HTTP client with rate limiting and retries."""

import logging
import time
from typing import Optional

import requests

from online_comment_crawler.config import (
    REQUEST_INTERVAL,
    REQUEST_RETRIES,
    REQUEST_TIMEOUT,
    USER_AGENT,
)

logger = logging.getLogger(__name__)

_session: Optional[requests.Session] = None
_last_request_time: float = 0.0


def _session_instance() -> requests.Session:
    global _session
    if _session is None:
        _session = requests.Session()
        _session.headers["User-Agent"] = USER_AGENT
    return _session


def get(url: str, cookies: Optional[dict] = None) -> str:
    """
    GET url with rate limiting and retries. Returns response text.
    Raises on final failure after retries.
    """
    global _last_request_time
    session = _session_instance()
    if cookies:
        session.cookies.update(cookies)

    for attempt in range(REQUEST_RETRIES):
        now = time.monotonic()
        elapsed = now - _last_request_time
        if elapsed < REQUEST_INTERVAL:
            time.sleep(REQUEST_INTERVAL - elapsed)
        _last_request_time = time.monotonic()

        try:
            resp = session.get(url, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            return resp.text
        except requests.RequestException as e:
            logger.warning("Request attempt %s/%s failed: %s", attempt + 1, REQUEST_RETRIES, e)
            if attempt == REQUEST_RETRIES - 1:
                raise
            time.sleep(1.0 * (attempt + 1))
    raise RuntimeError("Unreachable")
