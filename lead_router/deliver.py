#!/usr/bin/env python3
"""
Lead Delivery Bot
Fetches qualified leads and sends formatted report.
"""

import sys
from datetime import datetime
from pathlib import Path

import pytz

sys.path.insert(0, str(Path(__file__).parent.parent))
from lead_router.fetcher import fetch_all_leads, format_lead
from lead_router.config import get_config


def main():
    """Main entry point."""
    config = get_config()
    tz = pytz.timezone(config.get('delivery.timezone', 'Asia/Almaty'))
    now = datetime.now(tz)
    
    print(f"🔍 Lead Scan — {now.strftime('%Y-%m-%d %H:%M')}")
    print()
    
    min_score = config.min_score
    max_leads = config.get('delivery.max_leads_per_batch', 10)
    
    results = fetch_all_leads(min_score=min_score)  # Tuned for AI-doability, Python/JS stack
    
    if not results:
        print("📭 No new qualified leads found since last check.")
        print()
        print("Qualification: AI-doable + $200+ budget + data/code deliverable")
        return
    
    # Header
    batch_size = min(max_leads, len(results))
    print(f"🎯 Found {len(results)} qualified leads (showing top {batch_size})")
    print()
    print("=" * 50)
    print()
    
    # Format each lead
    for result in results[:batch_size]:
        print(format_lead(result))
        print()
    
    # Footer
    if len(results) > batch_size:
        print(f"... and {len(results) - batch_size} more in queue")
        print()
    
    print("💡 Reply with lead number to draft a proposal, or 'skip' to dismiss batch.")


if __name__ == "__main__":
    main()
