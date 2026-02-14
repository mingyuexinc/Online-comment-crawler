"""Main flow: fetch pages, parse reviews, save to disk."""

import logging
from pathlib import Path

from online_comment_crawler.config import CrawlerConfig, apply_config, get_recommended_url
from online_comment_crawler.html_parser import parse_reviews
from online_comment_crawler.paginator import iter_review_pages
from online_comment_crawler.storage import save_reviews

logger = logging.getLogger(__name__)


def run_single_user_reviews(config: CrawlerConfig) -> None:
    """
    Crawl one user's recommended reviews and write each game's reviews to a txt file.
    All parameters come from config (user_id, output_dir, max_pages, etc.).
    output_dir supports both relative and absolute paths.
    """
    apply_config(config)
    uid = config.user_id
    if not uid:
        raise ValueError("user_id is required (set in config file)")
    out = config.output_dir
    # Resolve so that relative paths are relative to cwd; absolute stay absolute
    out = out.resolve()
    url = get_recommended_url(uid, use_vanity=config.use_vanity)
    logger.info("Starting crawl for user %s -> %s", uid, url)
    logger.info("Output directory: %s", out)
    out.mkdir(parents=True, exist_ok=True)
    total = 0
    for html, page in iter_review_pages(url, max_pages=config.max_pages):
        items = parse_reviews(html)
        if not items:
            logger.info("No reviews on page %s, stopping pagination.", page)
            break
        save_reviews(items, out)
        total += len(items)
        logger.info("Page %s: %s reviews, total so far %s", page, len(items), total)
    logger.info("Done. Total reviews written: %s", total)
