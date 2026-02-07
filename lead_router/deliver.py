#!/usr/bin/env python3
"""
Lead Delivery Bot
Fetches qualified leads and sends formatted report with hot offers.
"""

import sys
from datetime import datetime
from pathlib import Path

import pytz

sys.path.insert(0, str(Path(__file__).parent.parent))
from lead_router.fetcher import fetch_all_leads, format_lead
from lead_router.config import get_config


def generate_hot_offer(result) -> str:
    """Generate hot offer text for a lead."""
    gig_type = result.gig_type
    
    offers = {
        "scraping": {
            "demo": "10-min sample scrape (5-10 real rows)",
            "text": "🔥 **Hot Offer:** I'll pull 5-10 sample rows from a similar site right now — you'll see the exact data format before we proceed. Takes 10 min. Want me to run it?"
        },
        "bot": {
            "demo": "20-min demo bot deployment",
            "text": "🔥 **Hot Offer:** I'll deploy a working demo bot with basic commands in 20 minutes. Add it to your test server and try it immediately. If you like it — I'll customize. Deal?"
        },
        "extension": {
            "demo": "30-min prototype ZIP",
            "text": "🔥 **Hot Offer:** I'll build a working prototype in 30 min that functions on 1-2 sites. Install the ZIP and test. If the concept works — I'll polish it for your exact needs."
        },
        "integration": {
            "demo": "30-min webhook endpoint",
            "text": "🔥 **Hot Offer:** I'll set up a working webhook endpoint in 30 min. Send test data and see it process in real-time. Working demo > long description. Should I set it up?"
        },
        "ecommerce": {
            "demo": "20-min Loom video",
            "text": "🔥 **Hot Offer:** I'll record a 60-sec video in 20 min showing exactly how the automation works (test store). You see it before buying. Interested?"
        },
        "automation": {
            "demo": "20-min working script",
            "text": "🔥 **Hot Offer:** I'll build a working prototype script in 20 min that does the core task. You run it, see it work, then decide. Demo first, payment later. Sound fair?"
        },
    }
    
    default_offer = {
        "demo": "10-min research + plan",
        "text": "🔥 **Hot Offer:** I'll spend 10 minutes researching your specific need and come back with a concrete implementation plan + timeline. No generic proposals — specific solution."
    }
    
    offer = offers.get(gig_type, default_offer)
    return offer['text']


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
    
    # Format each lead with hot offer
    for i, result in enumerate(results[:batch_size], 1):
        print(f"#{i}")
        print(format_lead(result))
        print()
        
        # Add hot offer for good leads (score >= 40)
        if result.total_score >= 40:
            print(generate_hot_offer(result))
            print()
        
        print("-" * 70)
        print()
    
    # Footer
    if len(results) > batch_size:
        print(f"... and {len(results) - batch_size} more in queue")
        print()
    
    print("💡 Reply with lead number to get full outreach draft, or 'skip' to dismiss batch.")


if __name__ == "__main__":
    main()
