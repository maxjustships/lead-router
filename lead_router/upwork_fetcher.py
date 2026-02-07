#!/usr/bin/env python3
"""
Upwork RSS Fetcher
Generates and fetches from Upwork job search RSS feeds.
"""

import re
import sys
from pathlib import Path
from typing import List

import feedparser

sys.path.insert(0, str(Path(__file__).parent.parent))
from lead_router.scorer import Lead, score_lead, format_lead


# Pre-built Upwork RSS feed URLs for common searches
UPWORK_FEEDS = {
    "python-scraper": "https://www.upwork.com/nx/jobs/search/?q=python+scraper&sort=recency&rss=true",
    "web-automation": "https://www.upwork.com/nx/jobs/search/?q=web+automation&sort=recency&rss=true", 
    "chrome-extension": "https://www.upwork.com/nx/jobs/search/?q=chrome+extension&sort=recency&rss=true",
    "data-extraction": "https://www.upwork.com/nx/jobs/search/?q=data+extraction&sort=recency&rss=true",
    "api-integration": "https://www.upwork.com/nx/jobs/search/?q=api+integration&sort=recency&rss=true",
    "bot-development": "https://www.upwork.com/nx/jobs/search/?q=bot+development&sort=recency&rss=true",
    "shopify-app": "https://www.upwork.com/nx/jobs/search/?q=shopify+app&sort=recency&rss=true",
    "javascript-automation": "https://www.upwork.com/nx/jobs/search/?q=javascript+automation&sort=recency&rss=true",
}


def fetch_upwork_feed(feed_name: str, feed_url: str, limit: int = 10) -> List[Lead]:
    """Fetch leads from a single Upwork RSS feed."""
    leads = []
    
    try:
        # Set a browser-like User-Agent to avoid 403
        feed = feedparser.parse(
            feed_url,
            agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        
        if hasattr(feed, 'status') and feed.status != 200:
            print(f"⚠️  Upwork feed '{feed_name}' returned status {feed.status}")
            return leads
        
        for entry in feed.entries[:limit]:
            title = entry.get('title', '')
            desc = entry.get('summary', entry.get('description', ''))
            url = entry.get('link', '')
            
            # Extract budget from description
            budget = None
            budget_patterns = [
                r'\$[\d,]+(?:\.\d{2})?',
                r'\$\d+\s*-\s*\$?\d+',
                r'\$\d+\+',
                r'\$\d+k',
            ]
            for pattern in budget_patterns:
                match = re.search(pattern, desc)
                if match:
                    budget = match.group()
                    break
            
            # Also look for hourly hints
            if not budget:
                if re.search(r'\$\d+/hr|\$\d+ per hour|\$\d+ hourly', desc, re.I):
                    budget_match = re.search(r'\$\d+', desc)
                    if budget_match:
                        budget = budget_match.group() + "/hr"
            
            leads.append(Lead(
                source=f"Upwork/{feed_name}",
                title=title,
                description=desc,
                url=url,
                budget_hint=budget
            ))
            
    except Exception as e:
        print(f"❌ Error fetching Upwork/{feed_name}: {e}")
    
    return leads


def fetch_all_upwork(min_score: int = 40) -> List:
    """Fetch and score leads from all Upwork feeds."""
    all_leads = []
    
    print(f"🔍 Fetching {len(UPWORK_FEEDS)} Upwork feeds...")
    print()
    
    for feed_name, feed_url in UPWORK_FEEDS.items():
        leads = fetch_upwork_feed(feed_name, feed_url, limit=5)
        print(f"  📡 {feed_name}: {len(leads)} raw leads")
        all_leads.extend(leads)
    
    print()
    print(f"📊 Total raw leads: {len(all_leads)}")
    print()
    
    # Score and filter
    results = []
    for lead in all_leads:
        result = score_lead(lead)
        if result.total_score >= min_score:
            results.append(result)
    
    # Sort by score
    results.sort(key=lambda r: r.total_score, reverse=True)
    return results


def main():
    """Main entry point."""
    results = fetch_all_upwork(min_score=40)
    
    print(f"✅ Qualified leads: {len(results)}\n")
    print("=" * 60)
    print()
    
    for result in results[:10]:
        print(format_lead(result))
        print()


if __name__ == "__main__":
    main()
