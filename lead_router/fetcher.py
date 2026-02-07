#!/usr/bin/env python3
"""
Lead Fetcher - RSS/API aggregation
Fetches from Upwork RSS, Reddit API, IndieHackers RSS
"""

import feedparser
import hashlib
import json
import sys
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Set

from lead_router.scorer import Lead, score_lead, format_lead


# Storage for deduplication
SEEN_FILE = Path(__file__).parent.parent / ".seen_leads.json"


def load_seen() -> Set[str]:
    """Load previously seen lead IDs."""
    if SEEN_FILE.exists():
        with open(SEEN_FILE) as f:
            return set(json.load(f))
    return set()


def save_seen(seen: Set[str]) -> None:
    """Save seen lead IDs."""
    # Keep only last 1000 to prevent bloat
    recent = list(seen)[-1000:]
    with open(SEEN_FILE, 'w') as f:
        json.dump(recent, f)


def make_id(url: str) -> str:
    """Create a stable ID from URL."""
    return hashlib.md5(url.encode()).hexdigest()[:12]


def fetch_reddit_api(subreddit: str, keywords: List[str]) -> List[Lead]:
    """Fetch leads from Reddit using .json endpoint (no auth needed for public)."""
    leads = []
    
    try:
        url = f"https://www.reddit.com/r/{subreddit}/new.json?limit=25"
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'LeadBot/1.0 (Lead Aggregation)'}
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read())
            
        for post in data.get('data', {}).get('children', []):
            post_data = post['data']
            title = post_data.get('title', '')
            desc = post_data.get('selftext', '')
            url = f"https://reddit.com{post_data.get('permalink', '')}"
            
            # Check keywords (case insensitive)
            text = f"{title} {desc}".lower()
            if not any(kw.lower() in text for kw in keywords):
                continue
            
            # Only posts where someone is HIRING (not looking for work)
            title_lower = title.lower()
            is_hiring = '[hiring]' in title_lower or 'hiring]' in title_lower
            is_looking_to_hire = 'looking to hire' in text or 'need a developer' in text or 'need help with' in text
            
            # Reject [For Hire] posts
            if '[for hire]' in title_lower or '[forhire]' in title_lower:
                continue
            
            if not (is_hiring or is_looking_to_hire):
                continue
            
            # Extract budget from title or body
            budget = None
            import re
            budget_match = re.search(r'\$[\d,]+(?:-\$?[\d,]+)?|\$\d+k?', title + " " + desc)
            if budget_match:
                budget = budget_match.group()
            
            leads.append(Lead(
                source=f"Reddit r/{subreddit}",
                title=title,
                description=desc,
                url=url,
                budget_hint=budget
            ))
    except Exception as e:
        print(f"Error fetching Reddit r/{subreddit}: {e}", file=sys.stderr)
    
    return leads


def fetch_indiehackers_rss() -> List[Lead]:
    """Fetch from IndieHackers RSS."""
    leads = []
    keywords = ["looking for", "need developer", "build an app", "automation", "scraper", "mvp"]
    
    try:
        feed = feedparser.parse("https://www.indiehackers.com/rss")
        for entry in feed.entries[:15]:
            title = entry.get('title', '')
            desc = entry.get('summary', '')
            url = entry.get('link', '')
            
            text = f"{title} {desc}".lower()
            if not any(kw.lower() in text for kw in keywords):
                continue
            
            leads.append(Lead(
                source="IndieHackers",
                title=title,
                description=desc,
                url=url
            ))
    except Exception as e:
        print(f"Error fetching IndieHackers: {e}", file=sys.stderr)
    
    return leads


def fetch_all_leads(min_score: int = 40) -> List:
    """Fetch and score all leads from all sources."""
    all_leads = []
    
    # Reddit (no auth needed)
    reddit_subs = [
        ("forhire", ["[hiring]", "developer", "python", "scraper", "automation", "bot", "extension"]),
        ("slavelabour", ["[task]", "scraper", "automation", "script", "bot"]),
        ("webdev", ["[for hire]", "[hiring]", "javascript", "chrome extension", "api", "developer"]),
        ("Python", ["[for hire]", "[hiring]", "scraper", "automation", "script", "bot"]),
        ("sideproject", ["looking for", "need help", "developer", "build"]),
        ("jobbit", ["[hiring]", "remote", "python", "automation", "scraper"]),
    ]
    
    for sub, keywords in reddit_subs:
        all_leads.extend(fetch_reddit_api(sub, keywords))
    
    # IndieHackers
    all_leads.extend(fetch_indiehackers_rss())
    
    # Score and filter
    seen = load_seen()
    results = []
    new_ids = []
    
    for lead in all_leads:
        lead_id = make_id(lead.url)
        if lead_id in seen:
            continue
        
        result = score_lead(lead)
        if result.total_score >= min_score:
            results.append(result)
        
        new_ids.append(lead_id)
    
    # Update seen
    seen.update(new_ids)
    save_seen(seen)
    
    # Sort by score descending
    results.sort(key=lambda r: r.total_score, reverse=True)
    return results


def main():
    """Main entry point for CLI usage."""
    results = fetch_all_leads(min_score=70)
    
    if not results:
        print("No new qualified leads found.")
        sys.exit(0)
    
    print(f"Found {len(results)} qualified leads:\n")
    for result in results[:10]:
        print(format_lead(result))
        print()


if __name__ == "__main__":
    main()
