#!/usr/bin/env python3
"""
Lead Router - Main entry point
AI-powered lead aggregation and qualification system
"""

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lead_router.fetcher import fetch_all_leads
from lead_router.scorer import format_lead
from lead_router.config import get_config, reload_config


def main():
    """Main entry point."""
    # Load config first to get defaults
    config = get_config()
    
    parser = argparse.ArgumentParser(
        description="Lead Router - AI-powered lead aggregation"
    )
    parser.add_argument(
        "--min-score",
        type=int,
        default=config.min_score,
        help=f"Minimum qualification score (default: {config.min_score})"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=config.get('delivery.max_leads_per_batch', 10),
        help="Maximum leads to display"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Reload config from file before run"
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to custom config file"
    )
    
    args = parser.parse_args()
    
    # Handle custom config path via env var
    if args.config:
        os.environ['LEAD_ROUTER_CONFIG_PATH'] = args.config
        reload_config()
    elif args.reload:
        reload_config()
        print("🔄 Config reloaded")
    
    print("🔍 Lead Router - Starting scan...")
    print()
    
    results = fetch_all_leads(min_score=args.min_score)
    
    if not results:
        print("📭 No qualified leads found.")
        return 0
    
    print(f"🎯 Found {len(results)} qualified leads (showing top {min(args.limit, len(results))})")
    print("=" * 60)
    print()
    
    for result in results[:args.limit]:
        print(format_lead(result))
        print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
