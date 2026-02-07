#!/usr/bin/env python3
"""
Lead Scoring Engine
Qualifies leads based on AI-doability, payment tier, tech stack, and urgency.
Supports: Scraping, Bots, Chrome Extensions, API Integrations, Shopify/WooCommerce
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
    gig_type: str  # scraping, bot, extension, integration, ecommerce, workflow


# Gig type detection patterns
GIG_PATTERNS = {
    "scraping": {
        "keywords": ["scrape", "scraping", "extract", "crawl", "data extraction", 
                     "pull data", "harvest", "collect data", "gather data"],
        "emoji": "🕷️",
        "name": "Data Scraping"
    },
    "bot": {
        "keywords": ["discord bot", "telegram bot", "slack bot", "twitter bot", 
                     "bot development", "chatbot", "automated messaging", 
                     "bot for", "create a bot", "build a bot"],
        "emoji": "🤖",
        "name": "Bot Development"
    },
    "extension": {
        "keywords": ["chrome extension", "browser extension", "firefox addon", 
                     "safari extension", "browser plugin"],
        "emoji": "🧩",
        "name": "Browser Extension"
    },
    "integration": {
        "keywords": ["api integration", "connect", "integrate", "webhook", 
                     "sync data", "n8n", "make.com", "zapier", "automate workflow",
                     "third-party api", "rest api"],
        "emoji": "🔗",
        "name": "API Integration"
    },
    "ecommerce": {
        "keywords": ["shopify", "woocommerce", "etsy", "bigcommerce", "magento",
                     "prestashop", "opencart", "ecommerce", "online store"],
        "emoji": "🛒",
        "name": "E-commerce"
    },
    "automation": {
        "keywords": ["automation", "automate", "script", "cron job", 
                     "scheduled task", "batch process"],
        "emoji": "⚙️",
        "name": "Automation"
    }
}


def detect_gig_type(text: str) -> str:
    """Detect the primary gig type from text."""
    text_lower = text.lower()
    scores = {}
    
    for gig_type, config in GIG_PATTERNS.items():
        score = sum(1 for kw in config["keywords"] if kw in text_lower)
        if score > 0:
            scores[gig_type] = score
    
    if not scores:
        return "general"
    
    return max(scores, key=scores.get)


def score_lead(lead: Lead) -> ScoreResult:
    """Score a single lead across all criteria."""
    reasons = []
    text = f"{lead.title} {lead.description}".lower()
    
    # Detect gig type
    gig_type = detect_gig_type(text)
    if gig_type in GIG_PATTERNS:
        config = GIG_PATTERNS[gig_type]
        reasons.append(f"{config['emoji']} Type: {config['name']}")
    
    # AI Doability (50 points max) - TOP PRIORITY
    ai_score = 0
    
    # Base positive indicators (apply to all gig types)
    base_indicators = [
        "specific", "clear requirements", "well defined", "detailed",
        "single task", "mvp", "prototype", "proof of concept"
    ]
    
    # Gig-specific indicators
    gig_indicators = {
        "scraping": ["csv", "json", "excel", "structured data", "export", 
                     "parse", "selector", "xpath", "css"],
        "bot": ["api token", "webhook", "slash command", "message handler",
                "notification", "alert", "monitor"],
        "extension": ["popup", "content script", "background script", 
                      "manifest v3", "browser action"],
        "integration": ["oauth", "api key", "endpoint", "payload", 
                        "request", "response", "json"],
        "ecommerce": ["product sync", "inventory", "order", "payment",
                      "checkout", "fulfillment"],
        "automation": ["schedule", "trigger", "condition", "action",
                       "input", "output", "transform"]
    }
    
    # Score base indicators
    for indicator in base_indicators:
        if indicator in text:
            ai_score += 3
    
    # Score gig-specific indicators
    specific_indicators = gig_indicators.get(gig_type, [])
    for indicator in specific_indicators:
        if indicator in text:
            ai_score += 5
            if ai_score >= 50:
                break
    
    # Universal positive signals
    universal_signals = ["documentation provided", "mockups", "wireframes", 
                         "examples", "sample output", "test data"]
    for signal in universal_signals:
        if signal in text:
            ai_score += 8
            reasons.append(f"✨ Bonus: {signal}")
    
    # Negative indicators
    negative_indicators = [
        "consultant", "advisor", "strategy", "long term",
        "partnership", "equity", "co-founder", "vague",
        "design", "logo", "branding", "marketing campaign",
        "rust", "c++", "c programming", "embedded", "systems",
        "full-time", "part-time position", "hire employee"
    ]
    
    for indicator in negative_indicators:
        if indicator in text:
            ai_score -= 15
            reasons.append(f"⚠️ Negative: '{indicator}'")
    
    ai_score = max(0, min(50, ai_score))
    if ai_score >= 35:
        reasons.append(f"✅ AI-doable ({ai_score}/50)")
    
    # Tech Stack Match (25 points max)
    tech_score = 0
    
    # Preferred stack for all gigs
    preferred_stack = ["python", "javascript", "typescript", "js", "ts", "node", "node.js"]
    
    # Gig-specific preferred tech
    gig_tech = {
        "scraping": ["beautifulsoup", "scrapy", "selenium", "playwright", "requests"],
        "bot": ["discord.py", "telebot", "python-telegram-bot", "slack-sdk", "discord.js"],
        "extension": ["chrome", "manifest", "content script", "popup"],
        "integration": ["n8n", "zapier", "make.com", "webhook", "rest api", "graphql"],
        "ecommerce": ["shopify api", "woocommerce api", "liquid", "php"],
        "automation": ["n8n", "zapier", "make.com", "airflow", "prefect"]
    }
    
    # Score general stack
    pref_matches = sum(1 for s in preferred_stack if s in text)
    tech_score += min(15, pref_matches * 3)
    
    # Score gig-specific tech
    specific_tech = gig_tech.get(gig_type, [])
    tech_matches = sum(1 for s in specific_tech if s in text)
    tech_score += min(15, tech_matches * 5)
    
    if pref_matches > 0:
        reasons.append(f"💻 Preferred stack ({pref_matches}): Python/JS/TS")
    if tech_matches > 0:
        reasons.append(f"🔧 {GIG_PATTERNS.get(gig_type, {}).get('name', 'Tech')} tools ({tech_matches})")
    
    # Avoid stack penalty
    avoid_stack = ["rust", "c++", "c#", "embedded", "systems programming", "kernel", "low-level"]
    avoid_matches = sum(1 for s in avoid_stack if s in text)
    if avoid_matches > 0:
        tech_score -= 25
        reasons.append(f"⛔ Avoid stack: Rust/C++/systems")
    
    tech_score = max(0, min(25, tech_score))
    
    # Urgency Signals (10 points max)
    urgency_score = 0
    urgency_words = ["asap", "urgent", "immediately", "quick turnaround", "this week", "today", "deadline", "rush"]
    
    for word in urgency_words:
        if word in text:
            urgency_score += 5
            reasons.append(f"⚡ Urgency: '{word}'")
            if urgency_score >= 10:
                break
    
    urgency_score = min(10, urgency_score)
    
    # Payment Tier (15 points max)
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
    elif any(word in text for word in ["paid", "pay", "budget", "compensation", "rate", "hourly", "fixed price"]):
        payment_score = 6
        reasons.append("💵 Paid work (amount unclear)")
    else:
        payment_score = 3
        reasons.append("💵 Payment status unclear")
    
    # Red flags
    red_flags = ["no budget", "exposure", "portfolio piece", "for free", "unpaid", "revenue share"]
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
        reasons=reasons,
        gig_type=gig_type
    )


def format_lead(result: ScoreResult) -> str:
    """Format a scored lead for display."""
    type_emoji = GIG_PATTERNS.get(result.gig_type, {}).get("emoji", "📋")
    
    lines = [
        f"{type_emoji} **[{result.lead.title}]({result.lead.url})**",
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
    test_cases = [
        Lead(
            source="reddit/r/forhire",
            title="[Hiring] Need a Python scraper for e-commerce site ASAP",
            description="Looking for someone to scrape product data from a Shopify store and deliver as CSV using Python. Budget is $300-500. Need this done this week.",
            url="https://reddit.com/r/forhire/example1",
            budget_hint="$300-500"
        ),
        Lead(
            source="reddit/r/forhire",
            title="[Hiring] Discord bot for crypto price alerts",
            description="Need a Discord bot that monitors crypto prices and sends alerts when certain thresholds are hit. Using CoinGecko API. Budget $400-600.",
            url="https://reddit.com/r/forhire/example2",
            budget_hint="$400-600"
        ),
        Lead(
            source="reddit/r/webdev",
            title="[Hiring] Chrome extension for productivity tracking",
            description="Build a Chrome extension that tracks time spent on websites and shows daily reports. Manifest V3. Budget $500.",
            url="https://reddit.com/r/webdev/example3",
            budget_hint="$500"
        ),
        Lead(
            source="IndieHackers",
            title="Looking for developer to integrate Stripe with my SaaS",
            description="Need help integrating Stripe Checkout and webhooks into my Node.js app. Also need help with n8n automation for onboarding emails.",
            url="https://indiehackers.com/example4",
            budget_hint=None
        )
    ]
    
    for test_lead in test_cases:
        result = score_lead(test_lead)
        print(format_lead(result))
        print()


if __name__ == "__main__":
    main()
