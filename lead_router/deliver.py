#!/usr/bin/env python3
"""
Lead Delivery Bot - Clean output, no auto hot offers
User selects lead, then we generate custom hot offer + outreach
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
    
    results = fetch_all_leads(min_score=min_score)
    
    if not results:
        print("📭 No new qualified leads found since last check.")
        print()
        print("Qualification: AI-doable + budget mentioned + data/code deliverable")
        return
    
    # Header
    batch_size = min(max_leads, len(results))
    print(f"🎯 Found {len(results)} qualified leads (showing top {batch_size})")
    print()
    print("=" * 70)
    print()
    
    # Format each lead (no hot offers here!)
    for i, result in enumerate(results[:batch_size], 1):
        print(f"#{i}")
        print(format_lead(result))
        print("-" * 70)
        print()
    
    # Footer
    if len(results) > batch_size:
        print(f"... and {len(results) - batch_size} more in queue")
        print()
    
    print("💡 Reply with lead number (e.g., 'lead 3') and I'll:")
    print("   1. Generate custom hot offer demo idea")
    print("   2. Write outreach message")
    print("   3. Wait for your approval")
    print("   4. Send via browser when you say 'send'")


if __name__ == "__main__":
    main()
