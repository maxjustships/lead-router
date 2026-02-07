#!/usr/bin/env python3
"""
Lead Scoring Engine
Qualifies leads based on AI-doability, payment tier, tech stack, and urgency.
"""

import re
from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class Lead:
    """Represents a potential job lead."""
    source: str
    title: str
    description: str
    url: str
    budget_hint: Optional[str] = None
    raw_data: Optional[Dict] = None


@dataclass
class ScoreResult:
    """Result of scoring a lead."""
    lead: Lead
    total_score: int
    ai_doable_score: int
    payment_score: int
    tech_match_score: int
    reasons: List[str]


def score_lead(lead: Lead) -> ScoreResult:
    """Score a single lead across all criteria."""
    reasons = []
    
    # AI Doability (50 points max) - TOP PRIORITY
    ai_score = 0
    text = f"{lead.title} {lead.description}".lower()
    
    positive_indicators = [
        "scrape", "extract", "automation", "bot", "script",
        "csv", "json", "excel", "api integration", "chrome extension",
        "specific", "clear requirements", "well defined",
        "data", "export", "convert", "parse", "crawl",
        "webhook", "integration", "dashboard", "mvp", "prototype"
    ]
    negative_indicators = [
        "consultant", "advisor", "strategy", "long term",
        "partnership", "equity", "co-founder", "vague",
        "design", "logo", "branding", "marketing", 
        "rust", "c++", "c programming", "embedded", "systems"
    ]
    
    for indicator in positive_indicators:
        if indicator in text:
            ai_score += 5
            if ai_score >= 50:
                break
    
    for indicator in negative_indicators:
        if indicator in text:
            ai_score -= 15
            reasons.append(f"⚠️ Negative: '{indicator}'")
    
    ai_score = max(0, min(50, ai_score))
    if ai_score >= 35:
        reasons.append(f"✅ AI-doable ({ai_score}/50)")
    
    # Tech Stack Match (25 points max) - Prefer Python/JS/TS
    tech_score = 0
    
    preferred_stack = ["python", "javascript", "typescript", "js", "ts", "node", "node.js", "react"]
    acceptable_stack = ["web scraping", "chrome extension", "browser extension", "shopify", "wordpress", "api"]
    avoid_stack = ["rust", "c++", "c#", "embedded", "systems programming", "kernel", "low-level"]
    
    pref_matches = sum(1 for s in preferred_stack if s in text)
    ok_matches = sum(1 for s in acceptable_stack if s in text)
    avoid_matches = sum(1 for s in avoid_stack if s in text)
    
    if pref_matches > 0:
        tech_score += min(20, pref_matches * 5)
        reasons.append(f"💻 Preferred stack ({pref_matches}): Python/JS/TS")
    
    if ok_matches > 0:
        tech_score += min(10, ok_matches * 3)
        reasons.append(f"📦 Acceptable stack ({ok_matches})")
    
    if avoid_matches > 0:
        tech_score -= 25
        reasons.append(f"⛔ Avoid stack detected: Rust/C++/systems")
    
    tech_score = max(0, min(25, tech_score))
    
    # Urgency Signals (10 points max)
    urgency_score = 0
    urgency_words = ["asap", "urgent", "immediately", "quick turnaround", "this week", "today", "deadline"]
    
    for word in urgency_words:
        if word in text:
            urgency_score += 5
            reasons.append(f"⚡ Urgency: '{word}'")
            if urgency_score >= 10:
                break
    
    urgency_score = min(10, urgency_score)
    
    # Payment Tier (15 points max) - Any pay is fine
    payment_score = 0
    budget_text = lead.budget_hint or text
    
    high_budget = re.search(r'\$[\d,]{3,}(?:\+)?|\$\d+k', budget_text, re.I)
    mid_budget = re.search(r'\$\d{2,3}(?:\+)?', budget_text)
    low_budget = re.search(r'\$\d{1,2}(?:\+)?', budget_text)
    any_budget = re.search(r'\$\d+', budget_text)
    
    if high_budget:
        payment_score = 15
        reasons.append(f"💰 High budget: {high_budget.group()}")
    elif mid_budget:
        payment_score = 12
        reasons.append(f"💰 Decent budget: {mid_budget.group()}")
    elif low_budget:
        payment_score = 10
        reasons.append(f"💵 Small budget: {low_budget.group()}")
    elif any_budget:
        payment_score = 8
        reasons.append("💵 Budget mentioned")
    elif any(word in text for word in ["paid", "pay", "budget", "compensation", "rate", "hourly"]):
        payment_score = 6
        reasons.append("💵 Paid work (amount unclear)")
    else:
        payment_score = 3
        reasons.append("💵 Payment status unclear")
    
    # Penalty for free/exposure work only
    red_flags = ["no budget", "exposure", "portfolio piece", "for free", "unpaid"]
    for flag in red_flags:
        if flag in text:
            payment_score -= 10
            reasons.append(f"⚠️ Red flag: '{flag}'")
    
    payment_score = max(0, min(15, payment_score))
    
    total = ai_score + tech_score + urgency_score + payment_score
    
    return ScoreResult(
        lead=lead,
        total_score=total,
        ai_doable_score=ai_score,
        payment_score=payment_score,
        tech_match_score=tech_score + urgency_score,
        reasons=reasons
    )


def format_lead(result: ScoreResult) -> str:
    """Format a scored lead for display."""
    lines = [
        f"**[{result.lead.title}]({result.lead.url})**",
        f"📍 Source: {result.lead.source}",
        f"⭐ Score: {result.total_score}/100 (AI: {result.ai_doable_score}, Pay: {result.payment_score}, Tech: {result.tech_match_score})",
        "",
        f"📝 {result.lead.description[:200]}{'...' if len(result.lead.description) > 200 else ''}",
        "",
        "📋 Why it fits:",
    ]
    for reason in result.reasons:
        lines.append(f"  • {reason}")
    
    lines.append("")
    lines.append("---")
    return "\n".join(lines)


def main():
    """Test the scoring engine with sample data."""
    test_lead = Lead(
        source="reddit/r/forhire",
        title="[Hiring] Need a Python scraper for e-commerce site ASAP",
        description="Looking for someone to scrape product data from a Shopify store and deliver as CSV using Python. Budget is $300-500. Need this done this week.",
        url="https://reddit.com/r/forhire/example",
        budget_hint="$300-500"
    )
    
    result = score_lead(test_lead)
    print(format_lead(result))


if __name__ == "__main__":
    main()
