#!/usr/bin/env python3
"""CLI entry: crawl one Steam user's recommended reviews (config from config file)."""

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from online_comment_crawler.config import load_config
from online_comment_crawler.runner import run_single_user_reviews

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Crawl a Steam user's game reviews; parameters are read from config file."
    )
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        default=None,
        help="Path to config file (default: config.yaml in cwd or STEAM_CONFIG env).",
    )
    args = parser.parse_args()
    try:
        cfg = load_config(args.config)
    except FileNotFoundError as e:
        logging.error("%s", e)
        return 1
    except Exception as e:
        logging.exception("Failed to load config: %s", e)
        return 1
    try:
        run_single_user_reviews(cfg)
    except Exception as e:
        logging.exception("Crawl failed: %s", e)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
