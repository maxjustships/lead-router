#!/usr/bin/env python3
"""
Upwork Headless Browser Fetcher
Background job scanning using Playwright (no GUI, fully automated)
"""

import asyncio
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict

from playwright.async_api import async_playwright

sys.path.insert(0, str(Path(__file__).parent.parent))


# Upwork search URLs to monitor
UPWORK_SEARCHES = {
    "python-scraper": "https://www.upwork.com/nx/jobs/search/?q=python+scraper&sort=recency",
    "web-automation": "https://www.upwork.com/nx/jobs/search/?q=web+automation+script&sort=recency",
    "chrome-extension": "https://www.upwork.com/nx/jobs/search/?q=chrome+extension&sort=recency",
    "api-integration": "https://www.upwork.com/nx/jobs/search/?q=api+integration&sort=recency",
    "n8n-make": "https://www.upwork.com/nx/jobs/search/?q=n8n+make+automation&sort=recency",
}


async def fetch_upwork_jobs(search_name: str, search_url: str, limit: int = 5) -> List[Dict]:
    """Fetch jobs from Upwork using headless browser."""
    jobs = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        )
        page = await context.new_page()
        
        try:
            print(f"🔍 Fetching {search_name}...")
            await page.goto(search_url, wait_until="networkidle", timeout=30000)
            
            # Wait for job cards to load
            await page.wait_for_selector('article[data-test="job-tile"]', timeout=10000)
            
            # Extract job data
            job_cards = await page.query_selector_all('article[data-test="job-tile"]')
            
            for card in job_cards[:limit]:
                try:
                    # Title
                    title_elem = await card.query_selector('h2 a')
                    title = await title_elem.inner_text() if title_elem else "Untitled"
                    href = await title_elem.get_attribute('href') if title_elem else ""
                    url = f"https://www.upwork.com{href}" if href.startswith('/') else href
                    
                    # Description
                    desc_elem = await card.query_selector('[data-test="job-description"]')
                    description = await desc_elem.inner_text() if desc_elem else ""
                    
                    # Budget
                    budget_elem = await card.query_selector('strong[data-test="budget"]')
                    if not budget_elem:
                        budget_elem = await card.query_selector('[data-test="job-type-label"]')
                    budget = await budget_elem.inner_text() if budget_elem else "Not specified"
                    
                    # Posted time
                    time_elem = await card.query_selector('[data-test="job-timestamp"]')
                    posted = await time_elem.inner_text() if time_elem else "Unknown"
                    
                    jobs.append({
                        "source": f"Upwork/{search_name}",
                        "title": title.strip(),
                        "description": description.strip()[:300],
                        "url": url,
                        "budget": budget.strip(),
                        "posted": posted.strip(),
                    })
                except Exception:
                    continue
                    
        except Exception as e:
            print(f"❌ Error fetching {search_name}: {e}")
        finally:
            await browser.close()
    
    return jobs


async def fetch_all_upwork() -> List[Dict]:
    """Fetch jobs from all Upwork searches."""
    all_jobs = []
    
    for name, url in UPWORK_SEARCHES.items():
        jobs = await fetch_upwork_jobs(name, url, limit=5)
        all_jobs.extend(jobs)
        await asyncio.sleep(2)  # Be nice to Upwork
    
    return all_jobs


def score_job(job: Dict) -> int:
    """Simple scoring for Upwork jobs."""
    score = 0
    text = f"{job['title']} {job['description']}".lower()
    
    # AI-doable indicators
    ai_signals = ["python", "scrap", "automation", "bot", "script", "api", "n8n", "make.com"]
    score += sum(5 for s in ai_signals if s in text)
    
    # Stack match
    stack_signals = ["javascript", "typescript", "node", "react", "beautifulsoup", "selenium"]
    score += sum(3 for s in stack_signals if s in text)
    
    # Payment hint
    budget = job.get('budget', '')
    if '$' in budget:
        try:
            amount = int(re.sub(r'[^\d]', '', budget))
            if amount >= 100:
                score += 10
            elif amount >= 50:
                score += 5
        except ValueError:
            pass
    
    return min(100, score)


def format_job(job: Dict, index: int) -> str:
    """Format a job for display."""
    score = score_job(job)
    lines = [
        f"#{index} **[{job['title']}]({job['url']})**",
        f"📍 Source: {job['source']}",
        f"💰 Budget: {job['budget']}",
        f"🕒 Posted: {job['posted']}",
        f"⭐ Score: {score}/100",
        "",
        f"📝 {job['description'][:150]}{'...' if len(job['description']) > 150 else ''}",
        "",
        "---",
    ]
    return "\n".join(lines)


async def main():
    """Main entry point."""
    print(f"🔍 Upwork Job Scan — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print()
    
    jobs = await fetch_all_upwork()
    
    if not jobs:
        print("📭 No jobs found.")
        return
    
    # Score and sort
    scored_jobs = [(job, score_job(job)) for job in jobs]
    scored_jobs.sort(key=lambda x: x[1], reverse=True)
    
    # Filter qualified (score >= 40)
    qualified = [(job, score) for job, score in scored_jobs if score >= 40]
    
    print(f"📊 Total: {len(jobs)} jobs | Qualified: {len(qualified)}")
    print()
    
    for i, (job, score) in enumerate(qualified[:10], 1):
        print(format_job(job, i))
        print()


if __name__ == "__main__":
    asyncio.run(main())
