#!/usr/bin/env python3
"""
Lead Router - Main entry point
AI-powered lead aggregation and qualification system
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lead_router.fetcher import fetch_all_leads
from lead_router.scorer import format_lead


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Lead Router - AI-powered lead aggregation"
    )
    parser.add_argument(
        "--min-score",
        type=int,
        default=40,
        help="Minimum qualification score (default: 40)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum leads to display (default: 10)"
    )
    
    args = parser.parse_args()
    
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
