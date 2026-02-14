"""Data models for parsed reviews."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ReviewItem:
    """Single parsed review."""

    game_name: str
    review_text: str
    app_id: Optional[str] = None
    created_at: Optional[str] = None
    recommend: Optional[bool] = None
