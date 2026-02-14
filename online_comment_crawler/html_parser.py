"""Parse Steam community review pages: /recommended (apphub_Card) and /reviews (review_box)."""

import logging
import re
from typing import List

from bs4 import BeautifulSoup

from online_comment_crawler.models import ReviewItem

logger = logging.getLogger(__name__)

# Profile /recommended page uses apphub_Card; profile /reviews page uses review_box.
CARD_SELECTORS = ["div.apphub_Card", "div.review_box"]

# Game name: store page link or div with game name text (apphub page).
GAME_NAME_SELECTORS = [
    "div.apphub_GameName a",
    "div.apphub_GameInfo a[href*='store.steampowered.com/app/']",
    "a.apphub_AppTitle",
]
# Review body: apphub page and profile reviews page.
REVIEW_TEXT_SELECTORS = [
    "div.apphub_ReviewText",
    "div.review_content",
    "div.apphub_CardContent",
    "div.review_box_content div.content",
    "div.review_box_content",
]
# App ID: store link or community app link (profile /reviews uses steamcommunity.com/app/ID).
APP_LINK_SELECTORS = [
    "a[href*='store.steampowered.com/app/']",
    "a[href*='steamcommunity.com/app/']",
]


def _normalize_text(tag) -> str:
    if tag is None:
        return ""
    text = tag.get_text(separator="\n", strip=True)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def _get_game_name(card: BeautifulSoup) -> str:
    for sel in GAME_NAME_SELECTORS:
        el = card.select_one(sel)
        if el:
            name = _normalize_text(el)
            if name and not name.startswith("http"):
                return name
            title = el.get("title") or ""
            if title:
                return title.strip()
            href = el.get("href") or ""
            match = re.search(r"/app/\d+/([^/]+)/?", href)
            if match:
                return re.sub(r"[_-]+", " ", match.group(1)).strip() or "Unknown"
    return "Unknown"


def _get_review_text(card: BeautifulSoup) -> str:
    for sel in REVIEW_TEXT_SELECTORS:
        el = card.select_one(sel)
        if el:
            text = _normalize_text(el)
            if len(text) > 10:
                return text
    for block in card.find_all(["div", "p"], class_=True):
        if "review" in (block.get("class") or []) or "content" in (block.get("class") or []):
            t = _normalize_text(block)
            if len(t) > 10:
                return t
    return ""


def _get_app_id(card: BeautifulSoup) -> str | None:
    for sel in APP_LINK_SELECTORS:
        a = card.select_one(sel)
        if a:
            href = a.get("href") or ""
            match = re.search(r"/app/(\d+)", href)
            if match:
                return match.group(1)
    return None


def parse_reviews(html: str) -> List[ReviewItem]:
    """
    Parse one page HTML and return list of ReviewItem.
    Tries apphub_Card (recommended page) then review_box (profile /reviews page).
    """
    soup = BeautifulSoup(html, "lxml")
    items: List[ReviewItem] = []
    cards = []
    for sel in CARD_SELECTORS:
        cards = soup.select(sel)
        if cards:
            break
    if not cards:
        for a in soup.find_all("a", href=re.compile(r"store\.steampowered\.com/app/\d+")):
            parent = a.find_parent("div", class_=re.compile(r"apphub|review|Card"))
            if not parent:
                parent = a.find_parent("div", recursive=True)
            if parent:
                cards = [parent]
                break
    for card in cards:
        app_id = _get_app_id(card)
        game_name = _get_game_name(card)
        review_text = _get_review_text(card)
        if not review_text and not game_name and not app_id:
            continue
        if (not game_name or game_name == "Unknown") and app_id:
            game_name = f"App_{app_id}"
        items.append(
            ReviewItem(
                game_name=game_name or "Unknown",
                review_text=review_text,
                app_id=app_id,
            )
        )
    return items


def has_next_page(html: str, base_url: str) -> bool:
    """Heuristic: check if page contains 'Next' link or page number for next page."""
    soup = BeautifulSoup(html, "lxml")
    for a in soup.find_all("a", href=True):
        href = a.get("href", "")
        if "p=" in href and base_url.split("?")[0] in href:
            return True
    page_links = soup.select("a.profile_paging_link, span.pagebtn")
    return len(page_links) > 0
