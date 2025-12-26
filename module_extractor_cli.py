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
        epilog="""
Examples:
  python module_extractor_cli.py --urls https://help.zluri.com/
  python module_extractor_cli.py --urls https://help.zluri.com/ https://www.chargebee.com/docs/2.0/
  python module_extractor_cli.py --urls https://help.zluri.com/ --provider local
        """
    )

    parser.add_argument(
        "--urls",
        nargs="+",
        required=True,
        help="One or more documentation URLs to process"
    )

    parser.add_argument(
        "--provider",
        choices=["openai", "anthropic", "local"],
        default="local",
        help="LLM provider to use (openai | anthropic | local)"
    )

    parser.add_argument(
        "--model",
        help="Optional model override (e.g. gpt-4o, llama3)"
    )

    parser.add_argument(
        "--max-depth",
        type=int,
        default=2,
        help="Maximum crawl depth (default: 2)"
    )

    parser.add_argument(
        "--max-pages",
        type=int,
        default=30,
        help="Maximum pages to crawl (default: 30)"
    )

    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay between requests (default: 1.0s)"
    )

    parser.add_argument(
        "--output",
        help="Output file path (default: output/modules_<timestamp>.json)"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    return parser.parse_args()


# -------------------------------
# MAIN FUNCTION
# -------------------------------
def main():
    args = parse_arguments()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    logger.info("=" * 60)
    logger.info("Pulse - Module Extraction AI Agent")
    logger.info("=" * 60)
    logger.info(f"URLs to process: {len(args.urls)}")
    for url in args.urls:
        logger.info(f"  - {url}")
    logger.info(f"Provider: {args.provider}")
    logger.info(f"Max depth: {args.max_depth}")
    logger.info(f"Max pages: {args.max_pages}")
    logger.info("=" * 60)

    try:
        # -------------------------------
        # Step 1: Crawl
        # -------------------------------
        logger.info("\n[1/2] Crawling documentation...")

        crawler = DocumentationCrawler(
            max_depth=args.max_depth,
            max_pages=args.max_pages,
            delay=args.delay
        )

        all_crawled_data = []

        for idx, url in enumerate(args.urls, 1):
            logger.info(f"\nCrawling URL {idx}/{len(args.urls)}: {url}")
            crawled = crawler.crawl(url)
            all_crawled_data.extend(crawled)
            logger.info(f"  → Extracted content from {len(crawled)} pages")

        if not all_crawled_data:
            logger.error("No pages were successfully crawled.")
            sys.exit(1)

        logger.info(f"\n✓ Total pages crawled: {len(all_crawled_data)}")

        # -------------------------------
        # Step 2: Extract modules
        # -------------------------------
        logger.info("\n[2/2] Extracting modules with AI...")

        extractor = ModuleExtractor(
            provider=args.provider,
            model=args.model
        )

        results = extractor.extract_modules(all_crawled_data)

        if not results:
            logger.error("Module extraction failed or returned empty results.")
            sys.exit(1)

        logger.info(f"✓ Extracted {len(results)} modules")

        # -------------------------------
        # Display summary
        # -------------------------------
        logger.info("\n" + "=" * 60)
        logger.info("EXTRACTION SUMMARY")
        logger.info("=" * 60)

        for i, module in enumerate(results, 1):
            logger.info(f"{i}. {module['module']}")
            logger.info(f"   Description: {module['Description']}")
            logger.info(f"   Submodules ({len(module['Submodules'])}):")
            for name in module["Submodules"]:
                logger.info(f"     - {name}")

        # -------------------------------
        # Save output
        # -------------------------------
        if args.output:
            output_path = Path(args.output)
        else:
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = output_dir / f"modules_{timestamp}.json"

        extractor.save_results(results, str(output_path))

        logger.info("\n" + "=" * 60)
        logger.info(f"✓ Results saved to: {output_path}")
        logger.info("=" * 60)

        print("\n" + "=" * 60)
        print("JSON OUTPUT")
        print("=" * 60)
        print(json.dumps(results, indent=2))

    except KeyboardInterrupt:
        logger.warning("\nOperation cancelled by user.")
        sys.exit(1)

    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
