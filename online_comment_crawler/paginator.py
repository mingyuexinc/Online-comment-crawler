"""Paginate over Steam user recommended review pages."""

import logging
import re
from typing import Generator, Tuple

from online_comment_crawler import http_client

logger = logging.getLogger(__name__)


def _next_page_url(base: str, page: int) -> str:
    """Append or replace p= for pagination. Steam uses ?p=1, ?p=2, ..."""
    if page <= 1:
        return base
    if "?" in base:
        base = re.sub(r"[?&]p=\d+", "", base)
        sep = "&" if "?" in base else "?"
    else:
        sep = "?"
    return f"{base}{sep}p={page}"


def iter_review_pages(
    start_url: str,
    max_pages: int = 500,
) -> Generator[Tuple[str, int], None, None]:
    """
    Yield (html, page_number) for each page. Caller parses and stops when no reviews.
    """
    base = start_url.split("?")[0].rstrip("/")
    for page in range(1, max_pages + 1):
        url = _next_page_url(base, page)
        logger.info("Fetching page %s: %s", page, url)
        try:
            html = http_client.get(url)
        except Exception as e:
            logger.error("Failed to fetch page %s: %s", page, e)
            raise
        yield html, page
