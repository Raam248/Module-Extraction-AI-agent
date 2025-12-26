#!/usr/bin/env python3
"""
Command-line Module Extractor
Usage: python module_extractor_cli.py --urls <url1> <url2> ...
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from datetime import datetime

from crawler import DocumentationCrawler
from module_extractor import ModuleExtractor

# -------------------------------
# Logging Setup
# -------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# -------------------------------
# Argument Parser
# -------------------------------
def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Extract modules and submodules from documentation URLs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("--urls", nargs="+", required=True)
    parser.add_argument("--provider", choices=["openai", "anthropic", "local"], default="local")
    parser.add_argument("--model", help="Optional model override")
    parser.add_argument("--max-depth", type=int, default=2)
    parser.add_argument("--max-pages", type=int, default=30)
    parser.add_argument("--delay", type=float, default=1.0)
    parser.add_argument("--output", help="Output JSON path")
    parser.add_argument("--verbose", action="store_true")

    return parser.parse_args()


# -------------------------------
# MAIN
# -------------------------------
def main():
    args = parse_arguments()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    logger.info("=" * 60)
    logger.info("Pulse - Module Extraction AI Agent")
    logger.info("=" * 60)

    for url in args.urls:
        logger.info(f"URL: {url}")

    logger.info(f"Provider: {args.provider}")
    logger.info(f"Max depth: {args.max_depth}")
    logger.info(f"Max pages: {args.max_pages}")
    logger.info("=" * 60)

    try:
        # -------------------------------
        # STEP 1 — Crawl
        # -------------------------------
        logger.info("\n[1/2] Crawling documentation...")

        crawler = DocumentationCrawler(
            max_depth=args.max_depth,
            max_pages=args.max_pages,
            delay=args.delay,
        )

        all_pages = []
        for i, url in enumerate(args.urls, 1):
            logger.info(f"Crawling {i}/{len(args.urls)}: {url}")
            pages = crawler.crawl(url)
            all_pages.extend(pages)

        if not all_pages:
            logger.error("No content was crawled.")
            sys.exit(1)

        logger.info(f"✓ Total pages crawled: {len(all_pages)}")

        # -------------------------------
        # STEP 2 — Extract
        # -------------------------------
        logger.info("\n[2/2] Extracting modules with AI...")

        extractor = ModuleExtractor(
            provider=args.provider,
            model=args.model
        )

        results = extractor.extract_modules(all_pages)

        if not results:
            logger.error("Module extraction failed or returned empty results.")
            sys.exit(1)

        logger.info(f"✓ Extracted {len(results)} modules")

        # -------------------------------
        # SAFE DISPLAY
        # -------------------------------
        logger.info("\n" + "=" * 60)
        logger.info("EXTRACTION SUMMARY")
        logger.info("=" * 60)

        for idx, module in enumerate(results, 1):
            name = module.get("module", "Unnamed Module")
            desc = module.get("Description", "No description")
            subs = module.get("Submodules", {})

            logger.info(f"{idx}. {name}")
            logger.info(f"   Description: {desc}")
            logger.info(f"   Submodules ({len(subs)}):")

            for sub in subs:
                logger.info(f"     - {sub}")

        # -------------------------------
        # SAVE OUTPUT
        # -------------------------------
        if args.output:
            output_path = Path(args.output)
        else:
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = output_dir / f"modules_{timestamp}.json"

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        logger.info("=" * 60)
        logger.info(f"✓ Results saved to: {output_path}")
        logger.info("=" * 60)

        print("\nJSON OUTPUT:")
        print(json.dumps(results, indent=2))

    except KeyboardInterrupt:
        logger.warning("Interrupted by user.")
        sys.exit(1)

    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
