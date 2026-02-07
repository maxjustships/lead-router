# Lead Router

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 🤖 AI-powered lead aggregation and qualification system for freelance developers

Lead Router automatically scans multiple freelance platforms (Reddit, IndieHackers, Upwork), scores opportunities by AI-doability, and delivers the best leads to your inbox twice daily.

**Now supporting: Scraping • Bots • Chrome Extensions • API Integrations • E-commerce • Automation Workflows**

## ✨ Features

- **Multi-source aggregation**: Reddit (r/forhire, r/slavelabour, r/discord_bots, r/Shopify_App_Dev), IndieHackers RSS, Upwork
- **Multi-gig type detection**: Automatically identifies scraping, bot, extension, integration, e-commerce, and automation gigs
- **AI-powered scoring**: Weighs AI-doability (50%), tech stack match (25%), urgency (10%), and budget (15%)
- **Gig-specific indicators**: Each gig type has custom scoring criteria for relevant tech and requirements
- **Smart deduplication**: Tracks seen leads to prevent spam
- **Headless browser support**: Playwright-based fetching for protected sites
- **Dynamic configuration**: YAML file + environment variables + CLI args
- **Cron-ready**: Designed to run on schedule via cron or similar

## 🎯 Supported Gig Types

| Type | Emoji | Keywords | Typical Budget |
|------|-------|----------|----------------|
| 🕷️ **Data Scraping** | 🕷️ | scrape, extract, crawl, data extraction | $200-500 |
| 🤖 **Bot Development** | 🤖 | discord bot, telegram bot, slack bot, chatbot | $300-800 |
| 🧩 **Browser Extension** | 🧩 | chrome extension, browser extension, manifest v3 | $400-1000 |
| 🔗 **API Integration** | 🔗 | api integration, webhook, n8n, zapier | $300-700 |
| 🛒 **E-commerce** | 🛒 | shopify, woocommerce, product sync | $500-1500 |
| ⚙️ **Automation** | ⚙️ | automation, workflow, cron job, script | $200-600 |

## 📊 Scoring System

| Criterion | Weight | Description |
|-----------|--------|-------------|
| AI Doability | 50% | Clear scope, well-defined requirements, gig-specific indicators |
| Tech Stack | 25% | Python/JS/TS preferred + gig-specific tools |
| Urgency | 10% | ASAP, urgent, deadline keywords |
| Payment | 15% | Budget mentioned and reasonable |

**Minimum qualifying score**: 40/100

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/yourusername/lead-router.git
cd lead-router

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```bash
# Fetch and display qualified leads
python3 -m lead_router

# Override min score via CLI
python3 -m lead_router --min-score 50

# Use environment variable
LEAD_ROUTER_QUALIFICATION_MIN_SCORE=60 python3 -m lead_router

# Custom config file
python3 -m lead_router --config /path/to/my-config.yaml

# Reload config without restart
python3 -m lead_router --reload
```

### Configuration

Edit `config.yaml` to customize sources and scoring:

```yaml
channels:
  reddit:
    enabled: true
    subreddits:
      - name: "forhire"
        keywords: ["[hiring]", "python", "scraper", "bot", "extension"]
      - name: "discord_bots"
        keywords: ["[hiring]", "bot", "discord"]
  
qualification:
  min_score: 40
  criteria:
    ai_doable:
      weight: 50
```

### Environment Variables

Override any config value with env vars using `LEAD_ROUTER_` prefix:

```bash
LEAD_ROUTER_QUALIFICATION_MIN_SCORE=50
LEAD_ROUTER_DELIVERY_MAX_LEADS_PER_BATCH=5
LEAD_ROUTER_CHANNELS_REDDIT_ENABLED=false
```

### Cron Setup

```cron
# Morning batch - 9:00 AM
0 9 * * * cd /path/to/lead-router && python3 -m lead_router

# Afternoon batch - 2:00 PM
0 14 * * * cd /path/to/lead-router && python3 -m lead_router
```

## 📁 Project Structure

```
lead-router/
├── lead_router/          # Main package
│   ├── __init__.py
│   ├── config.py         # Dynamic configuration (YAML + env + CLI)
│   ├── fetcher.py        # RSS/API aggregation
│   ├── scorer.py         # Lead qualification engine (multi-gig support)
│   ├── deliver.py        # Report generation
│   ├── main.py           # CLI entry point
│   ├── upwork_fetcher.py # Upwork RSS fetcher
│   └── upwork_headless.py # Playwright-based fetcher
├── config.yaml           # Configuration
├── requirements.txt      # Dependencies
├── .gitignore           # Git ignore rules
├── LICENSE              # MIT License
└── README.md            # This file
```

## 🔧 Requirements

- Python 3.10+
- Dependencies:
  - `feedparser` - RSS parsing
  - `pytz` - Timezone handling
  - `pyyaml` - Configuration parsing
  - `playwright` - Headless browser (optional, for Upwork)

## 📝 Example Output

```
🔍 Lead Scan — 2024-02-07 09:00

🎯 Found 7 qualified leads (showing top 5)
==================================================

🤖 **[Hiring] Discord bot for crypto price alerts**
📍 Source: Reddit r/forhire
⭐ Score: 82/100 (AI: 40, Pay: 15, Tech: 27)

📝 Need a Discord bot that monitors crypto prices and sends alerts...

📋 Why it fits:
  • 🤖 Type: Bot Development
  • ✅ AI-doable (40/50)
  • 💻 Preferred stack: Python/JS/TS
  • 🔧 Bot Development tools (2)
  • 💰 High budget: $400-600
  • ⚡ Urgency: 'ASAP'

---

🧩 **[Hiring] Chrome extension for productivity tracking**
📍 Source: Reddit r/webdev
⭐ Score: 78/100 (AI: 38, Pay: 15, Tech: 25)

📝 Build a Chrome extension that tracks time spent on websites...

📋 Why it fits:
  • 🧩 Type: Browser Extension
  • ✅ AI-doable (38/50)
  • 🔧 Browser Extension tools (2)
  • 💰 High budget: $500

---
```

## 🛡️ Ethical Considerations

- Respects robots.txt and rate limits
- Uses reasonable delays between requests
- Does not scrape authenticated/private content
- Designed for lead discovery, not data harvesting

## 📜 License

MIT License - see [LICENSE](LICENSE) file.

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional platform integrations (Fiverr, Freelancer, Twitter/X)
- Enhanced ML-based scoring
- Webhook/API delivery options
- Slack/Discord integrations
- Proposal auto-generation

## 🗺️ Roadmap

- [x] Multi-gig type detection
- [x] Dynamic configuration
- [ ] Proposal generator integration
- [ ] Client CRM tracking
- [ ] Earnings dashboard
- [ ] Automated proposal sending

---

Built with ❤️ by freelancers, for freelancers.
