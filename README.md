# Lead Router

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 🤖 AI-powered lead aggregation and qualification system for freelance developers

Lead Router automatically scans multiple freelance platforms (Reddit, IndieHackers, Upwork), scores opportunities by AI-doability, and delivers the best leads to your inbox twice daily.

## ✨ Features

- **Multi-source aggregation**: Reddit (r/forhire, r/slavelabour), IndieHackers RSS, Upwork
- **AI-powered scoring**: Weighs AI-doability (50%), tech stack match (25%), urgency (10%), and budget (15%)
- **Smart deduplication**: Tracks seen leads to prevent spam
- **Headless browser support**: Playwright-based fetching for protected sites
- **Configurable**: YAML-based configuration for all sources and criteria
- **Cron-ready**: Designed to run on schedule via cron or similar

## 📊 Scoring System

| Criterion | Weight | Description |
|-----------|--------|-------------|
| AI Doability | 50% | Clear scope, well-defined requirements, data extraction tasks |
| Tech Stack | 25% | Python/JavaScript/TypeScript preferred |
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
python3 lead_router/main.py

# Fetch from specific sources
python3 lead_router/fetcher.py --source reddit
python3 lead_router/upwork_headless.py
```

### Configuration

Edit `config.yaml` to customize:

```yaml
channels:
  reddit:
    enabled: true
    subreddits:
      - name: "forhire"
        keywords: ["[hiring]", "python", "scraper", "automation"]
  
qualification:
  min_score: 40
  criteria:
    ai_doable:
      weight: 50
```

### Cron Setup

```cron
# Morning batch - 9:00 AM
0 9 * * * cd /path/to/lead-router && python3 lead_router/deliver.py

# Afternoon batch - 2:00 PM
0 14 * * * cd /path/to/lead-router && python3 lead_router/deliver.py
```

## 📁 Project Structure

```
lead-router/
├── lead_router/          # Main package
│   ├── __init__.py
│   ├── fetcher.py        # RSS/API aggregation
│   ├── scorer.py         # Lead qualification engine
│   ├── deliver.py        # Report generation
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
  - `playwright` - Headless browser (optional, for Upwork)

## 📝 Example Output

```
🔍 Lead Scan — 2024-02-07 09:00

🎯 Found 7 qualified leads (showing top 5)
==================================================

**[Hiring] Python scraper for e-commerce site**
📍 Source: Reddit r/forhire
⭐ Score: 87/100 (AI: 45, Pay: 12, Tech: 30)

📝 Looking for someone to scrape product data from a Shopify store...

📋 Why it fits:
  • ✅ AI-doable (45/50)
  • 💻 Preferred stack: Python
  • 💰 Decent budget: $300-500
  • ⚡ Urgency: 'ASAP'

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
- Additional platform integrations (Fiverr, Freelancer)
- Enhanced ML-based scoring
- Webhook/API delivery options
- Slack/Discord integrations

---

Built with ❤️ by freelancers, for freelancers.
