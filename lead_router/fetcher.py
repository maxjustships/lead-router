#!/usr/bin/env python3
"""
Lead Fetcher - RSS/API aggregation
Fetches from Reddit, IndieHackers, HN, We Work Remotely, RemoteOK
"""

import feedparser
import hashlib
import json
import re
import sys
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Set

from lead_router.scorer import Lead, score_lead, format_lead
from lead_router.config import get_config


# Storage for deduplication
SEEN_FILE = Path(__file__).parent.parent / ".seen_leads.json"


# Load config
config = get_config()


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
    # Expanded keywords for all gig types
    keywords = config.get('channels.indiehackers.feeds.0.keywords', 
                         ["looking for", "need developer", "build an app", "automation", 
                          "scraper", "mvp", "bot", "integration", "api", "webhook",
                          "chrome extension", "discord", "telegram", "shopify"])
    
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


def fetch_hn_whoishiring() -> List[Lead]:
    """Fetch from Hacker News 'Who is Hiring' monthly thread."""
    leads = []
    
    try:
        # HN Algolia API - search for "Who is Hiring" posts
        url = "https://hn.algolia.com/api/v1/search?query=who+is+hiring&tags=story&hitsPerPage=5"
        
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'LeadBot/1.0'}
        )
        
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read())
        
        # Find the most recent who is hiring thread
        thread_id = None
        for hit in data.get('hits', []):
            title = hit.get('title', '').lower()
            if 'who is hiring' in title:
                thread_id = hit.get('objectID')
                break
        
        if not thread_id:
            return leads
        
        # Fetch comments from the thread
        comments_url = f"https://hn.algolia.com/api/v1/search?tags=comment,story_{thread_id}&hitsPerPage=100"
        req = urllib.request.Request(comments_url, headers={'User-Agent': 'LeadBot/1.0'})
        
        with urllib.request.urlopen(req, timeout=15) as response:
            comments_data = json.loads(response.read())
        
        # Keywords for filtering
        keywords = ["python", "javascript", "automation", "scraper", "bot", "api", 
                   "integration", "remote", "contract", "freelance", "part-time"]
        
        for comment in comments_data.get('hits', []):
            text = comment.get('text', '')
            text_lower = text.lower()
            
            # Check if relevant to our keywords
            if not any(kw in text_lower for kw in keywords):
                continue
            
            # Extract company/job info
            author = comment.get('author', 'Unknown')
            comment_id = comment.get('objectID')
            url = f"https://news.ycombinator.com/item?id={comment_id}"
            
            # Try to extract budget/salary info
            budget = None
            salary_match = re.search(r'\$[\d,]+k?|\$[\d,]+-\$?[\d,]+', text)
            if salary_match:
                budget = salary_match.group()
            
            # Clean HTML tags from text
            clean_text = re.sub(r'<[^\u003e]+>', ' ', text).strip()[:500]
            
            leads.append(Lead(
                source=f"HN Who is Hiring",
                title=f"Job post by {author}",
                description=clean_text,
                url=url,
                budget_hint=budget
            ))
            
    except Exception as e:
        print(f"Error fetching HN Who is Hiring: {e}", file=sys.stderr)
    
    return leads


def fetch_weworkremotely() -> List[Lead]:
    """Fetch from We Work Remotely RSS feed."""
    leads = []
    
    try:
        feed = feedparser.parse("https://weworkremotely.com/remote-jobs.rss")
        
        # Keywords for filtering
        keywords = ["python", "javascript", "developer", "engineer", "scraper", 
                   "automation", "bot", "api", "integration", "backend"]
        
        for entry in feed.entries[:30]:  # Check last 30 entries
            title = entry.get('title', '')
            desc = entry.get('summary', entry.get('description', ''))
            url = entry.get('link', '')
            
            text = f"{title} {desc}".lower()
            
            # Check keywords
            if not any(kw in text for kw in keywords):
                continue
            
            # Try to extract company name from title
            # Format usually: "Company: Job Title"
            company = "Unknown"
            if ':' in title:
                parts = title.split(':', 1)
                company = parts[0].strip()
                job_title = parts[1].strip()
            else:
                job_title = title
            
            leads.append(Lead(
                source="We Work Remotely",
                title=job_title,
                description=f"Company: {company}. {desc[:300]}",
                url=url
            ))
            
    except Exception as e:
        print(f"Error fetching We Work Remotely: {e}", file=sys.stderr)
    
    return leads


def fetch_remoteok() -> List[Lead]:
    """Fetch from RemoteOK API (public, no auth required)."""
    leads = []
    
    try:
        url = "https://remoteok.com/api"
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'LeadBot/1.0',
                'Accept': 'application/json'
            }
        )
        
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read())
        
        # First item is metadata, rest are jobs
        if len(data) <= 1:
            return leads
        
        jobs = data[1:]  # Skip metadata
        
        # Keywords for filtering
        keywords = ["python", "javascript", "scraper", "automation", "bot", 
                   "api", "integration", "backend", "developer", "engineer"]
        
        for job in jobs[:50]:  # Check last 50 jobs
            position = job.get('position', '')
            company = job.get('company', '')
            description = job.get('description', '')
            url = job.get('url', job.get('apply_url', ''))
            
            text = f"{position} {description}".lower()
            
            # Check keywords
            if not any(kw in text for kw in keywords):
                continue
            
            # Get salary info if available
            salary = job.get('salary', '')
            budget = salary if salary else None
            
            # Clean description
            clean_desc = re.sub(r'<[^\u003e]+>', ' ', description).strip()[:400]
            
            leads.append(Lead(
                source="RemoteOK",
                title=f"{position} at {company}",
                description=clean_desc,
                url=url,
                budget_hint=budget
            ))
            
    except Exception as e:
        print(f"Error fetching RemoteOK: {e}", file=sys.stderr)
    
    return leads


def fetch_peopleperhour() -> List[Lead]:
    """Fetch from PeoplePerHour RSS feed for freelance gigs."""
    leads = []
    
    try:
        # PeoplePerHour RSS for development jobs
        # URL format: https://www.peopleperhour.com/rss/jobs?q=python+developer
        urls_to_check = [
            "https://www.peopleperhour.com/rss/jobs?q=python+developer",
            "https://www.peopleperhour.com/rss/jobs?q=javascript+developer",
            "https://www.peopleperhour.com/rss/jobs?q=web+scraper",
            "https://www.peopleperhour.com/rss/jobs?q=automation+bot",
        ]
        
        keywords = ["python", "javascript", "scraper", "automation", "bot", 
                   "api", "integration", "webhook", "script", "developer"]
        
        for rss_url in urls_to_check:
            try:
                feed = feedparser.parse(rss_url)
                
                for entry in feed.entries[:10]:  # Top 10 from each feed
                    title = entry.get('title', '')
                    desc = entry.get('summary', entry.get('description', ''))
                    url = entry.get('link', '')
                    
                    text = f"{title} {desc}".lower()
                    
                    # Check if relevant
                    if not any(kw in text for kw in keywords):
                        continue
                    
                    # Extract budget if mentioned
                    budget = None
                    budget_match = re.search(r'\$[\d,]+(?:-\$?[\d,]+)?|\$\d+', title + " " + desc)
                    if budget_match:
                        budget = budget_match.group()
                    
                    leads.append(Lead(
                        source="PeoplePerHour",
                        title=title,
                        description=desc[:400],
                        url=url,
                        budget_hint=budget
                    ))
                    
            except Exception as e:
                print(f"Error fetching PPH feed {rss_url}: {e}", file=sys.stderr)
                continue
                
    except Exception as e:
        print(f"Error fetching PeoplePerHour: {e}", file=sys.stderr)
    
    return leads


def fetch_simplyhired() -> List[Lead]:
    """Fetch from SimplyHired for freelance/contract gigs."""
    leads = []
    
    try:
        # SimplyHired RSS feed for remote freelance jobs
        # URL format: https://www.simplyhired.com/search?q=python+developer&rbs=50&tm=0&t=4
        # t=4 means freelance/contract
        rss_url = "https://www.simplyhired.com/search?q=python+developer+freelance&rbs=50&tm=0&t=4&fdb=7"
        
        feed = feedparser.parse(rss_url)
        
        keywords = ["python", "javascript", "scraper", "automation", "bot", 
                   "api", "integration", "freelance", "contract", "remote"]
        
        for entry in feed.entries[:15]:
            title = entry.get('title', '')
            desc = entry.get('summary', entry.get('description', ''))
            url = entry.get('link', '')
            
            text = f"{title} {desc}".lower()
            
            # Check if relevant
            if not any(kw in text for kw in keywords):
                continue
            
            # Extract budget/salary
            budget = None
            budget_match = re.search(r'\$[\d,]+(?:k|K)?(?:/hr| per hour| hourly)?', title + " " + desc)
            if budget_match:
                budget = budget_match.group()
            
            leads.append(Lead(
                source="SimplyHired",
                title=title,
                description=desc[:400],
                url=url,
                budget_hint=budget
            ))
            
    except Exception as e:
        print(f"Error fetching SimplyHired: {e}", file=sys.stderr)
    
    return leads


def fetch_guru() -> List[Lead]:
    """Fetch from Guru.com freelance jobs."""
    leads = []
    
    try:
        # Guru RSS for development jobs
        rss_url = "https://www.guru.com/rss/jobs/skill/python,web-development,automation/"
        
        feed = feedparser.parse(rss_url)
        
        keywords = ["python", "javascript", "scraper", "automation", "bot", 
                   "api", "integration", "webhook", "script"]
        
        for entry in feed.entries[:15]:
            title = entry.get('title', '')
            desc = entry.get('summary', entry.get('description', ''))
            url = entry.get('link', '')
            
            text = f"{title} {desc}".lower()
            
            # Check if relevant
            if not any(kw in text for kw in keywords):
                continue
            
            # Extract budget
            budget = None
            budget_match = re.search(r'\$[\d,]+(?:-\$?[\d,]+)?|\$\d+', title + " " + desc)
            if budget_match:
                budget = budget_match.group()
            
            leads.append(Lead(
                source="Guru",
                title=title,
                description=desc[:400],
                url=url,
                budget_hint=budget
            ))
            
    except Exception as e:
        print(f"Error fetching Guru: {e}", file=sys.stderr)
    
    return leads


def fetch_all_leads(min_score: int = None) -> List:
    """Fetch and score all leads from all sources."""
    global config
    
    # Use config if min_score not provided
    if min_score is None:
        min_score = config.min_score
    
    all_leads = []
    
    # Reddit subreddits - freelance focused with rate limiting
    reddit_subs = [
        # Primary hiring subreddits
        ("forhire", ["[hiring]", "developer", "python", "scraper", "automation", "bot", "extension", 
                     "integration", "discord", "telegram", "api", "shopify", "freelance"]),
        ("slavelabour", ["[task]", "scraper", "automation", "script", "bot", "simple", "quick"]),
        ("webdev", ["[hiring]", "javascript", "chrome extension", "api", 
                    "developer", "integration", "webhook", "frontend", "react"]),
        ("Python", ["[hiring]", "python", "scraper", "automation", "script", 
                    "bot", "discord", "telegram", "django", "flask"]),
        
        # Bot/Extension specific
        ("discord_bots", ["[hiring]", "bot", "discord", "automation", "telegram", "slack"]),
        ("Shopify_App_Dev", ["[hiring]", "shopify", "app", "integration", "api", "ecommerce"]),
        
        # Project/MVP focused
        ("sideproject", ["looking for", "need help", "developer", "build", "mvp", "automation"]),
        ("startups", ["looking for", "need developer", "build", "mvp", "prototype", "beta"]),
        
        # Alternative hiring
        ("jobbit", ["[hiring]", "remote", "python", "automation", "scraper", "bot", "contract"]),
        ("hireaprogrammer", ["[hiring]", "developer", "programmer", "script", "automation", "bot", "extension"]),
        
        # Small tasks / quick gigs
        ("beermoney", ["[hiring]", "script", "automation", "bot", "scraper", "tool"]),
        ("WorkOnline", ["[hiring]", "remote", "developer", "freelance", "contract", "python"]),
        
        # Specialized
        ("javascript", ["[hiring]", "javascript", "typescript", "node", "react", "extension"]),
        ("datascience", ["[hiring]", "python", "scraper", "data", "automation", "api", "pandas"]),
        ("web_design", ["[hiring]", "web", "developer", "frontend", "javascript", "shopify"]),
        ("SmallBusiness", ["looking for", "need help", "automation", "website", "shopify", "integration"]),
    ]
    
    # Rate limiting: Add delay between requests (respect Reddit API limits)
    import time
    for sub, keywords in reddit_subs:
        leads = fetch_reddit_api(sub, keywords)
        all_leads.extend(leads)
        time.sleep(0.5)  # 500ms delay between subreddits
    
    # IndieHackers (RSS - no rate limit concerns)
    if config.indiehackers_enabled:
        all_leads.extend(fetch_indiehackers_rss())
        time.sleep(0.2)
    
    # Low-hanging fruit: HN, WWR, RemoteOK (with rate limiting)
    if config.get('channels.hn.enabled', True):
        all_leads.extend(fetch_hn_whoishiring())
        time.sleep(1)  # HN Algolia has stricter limits
    if config.get('channels.weworkremotely.enabled', True):
        all_leads.extend(fetch_weworkremotely())
        time.sleep(0.5)
    if config.get('channels.remoteok.enabled', True):
        all_leads.extend(fetch_remoteok())
        time.sleep(0.5)
    
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
