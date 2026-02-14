"""Save review text to local txt files, one file per game."""

import logging
import re
from pathlib import Path

from online_comment_crawler.models import ReviewItem

logger = logging.getLogger(__name__)

# Characters not allowed in Windows/file names.
INVALID_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
MAX_FILENAME_LEN = 200


def _safe_filename(name: str, app_id: str | None = None) -> str:
    """Make a safe filename from game name; truncate and optionally add hash."""
    s = INVALID_CHARS.sub("_", name).strip() or "Unknown"
    s = re.sub(r"_+", "_", s)[:MAX_FILENAME_LEN].strip("_")
    if not s:
        s = "Unknown"
    if app_id:
        s = f"{s}_{app_id}"
    return s


def save_review(review: ReviewItem, output_dir: Path) -> None:
    """
    Append this review's text to a txt file named by game.
    Creates output_dir if needed. File name is sanitized from game_name.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    base = _safe_filename(review.game_name, review.app_id)
    path = output_dir / f"{base}.txt"
    sep = "\n\n---\n\n"
    content = review.review_text.strip()
    if not content:
        return
    if path.exists():
        with open(path, "a", encoding="utf-8") as f:
            f.write(sep)
            f.write(content)
            f.write("\n")
    else:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
            f.write("\n")
    logger.debug("Wrote review to %s", path)


def save_reviews(reviews: list[ReviewItem], output_dir: Path) -> None:
    """Save each review to the appropriate game file."""
    for r in reviews:
        save_review(r, output_dir)
