# Research Agent

**Extract structured data from websites using AI-powered prompts and schemas — plus LinkedIn and prospect research.**

Extract comprehensive company intelligence using 34 specialized prompts, Firecrawl + Claude, and optional LinkedIn (Bright Data) integration.

## Features

### Enrichment (Prompt + Schema Extraction)
- ✅ **34 Production-Ready Prompts** - Cover all aspects of a company
- ✅ **30 Matching Schemas** - Structured data extraction
- ✅ **Firecrawl Integration** - High-quality website scraping
- ✅ **Claude AI Extraction** - LLM-powered data extraction
- ✅ **Batch Processing** - Process multiple companies at once
- ✅ **Flexible Variables** - Pass custom data to prompts

### Prospect Research
- 🌐 **Website + LinkedIn** - Combine Firecrawl website data with LinkedIn company data
- 📊 **Google Sheets Export** - Export research to spreadsheets
- 🔗 **LinkedIn Profile** - Fetch individual LinkedIn profiles (Bright Data / Apify)

## Quick Start

```bash
cd research-agent

# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
# Edit .env with your API keys

# Extract company profile (enrichment)
python cli.py enrich https://stripe.com \
  --schema company_profile \
  --prompt extract_company \
  --company "Stripe"

# Research a company (website + LinkedIn)
python cli.py research "Acme Corp" \
  --website https://acme.com \
  --linkedin https://linkedin.com/company/acme

# List all available prompts
python cli.py list-prompts

# List all available schemas
python cli.py list-schemas

# Check configuration
python cli.py config-check
```

## Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `FIRECRAWL_API_KEY` | Yes (enrichment/research) | Get from https://firecrawl.dev |
| `ANTHROPIC_API_KEY` | Yes (enrichment) | Get from https://anthropic.com |
| `BRIGHTDATA_API_KEY` | Optional (LinkedIn) | For LinkedIn company/profile data |
| `APIFY_API_KEY` | Optional (LinkedIn fallback) | Alternative LinkedIn source |
| `GOOGLE_CREDENTIALS_PATH` | Optional (Sheets) | Path to service account JSON for Google Sheets |

## CLI Commands Overview

| Command | Description |
|---------|-------------|
| `list-prompts` | List all prompt templates |
| `list-schemas` | List all extraction schemas |
| `enrich` | Enrich a single URL (prompt + schema) |
| `batch` | Batch enrich from CSV |
| `research` | Full prospect research (website + LinkedIn) |
| `linkedin-profile` | Fetch a single LinkedIn profile |
| `config-check` | Verify API keys and credentials |

---

## 34 Available Prompts (Enrichment)

### Core Business (10)
- `extract_company` - Company profile and basics
- `extract_leadership` - Leadership team and executives
- `extract_hiring` - Job openings and growth signals
- `extract_customers` - Testimonials and case studies
- `extract_funding` - Investment and financial data
- `extract_geography` - Geographic presence
- `extract_icp` - Ideal customer profile
- `extract_competitors` - Competitive landscape
- `extract_press` - Media coverage and PR
- `extract_acquisitions` - M&A activity

### Product & Technology (8)
- `extract_product_features` - Features and capabilities
- `extract_tech_stack` - Technology and infrastructure
- `extract_api` - API and developer resources
- `extract_integrations` - Integrations and partnerships
- `extract_mobile` - Mobile app presence
- `extract_innovation` - R&D and innovation
- `extract_roadmap` - Product vision and roadmap
- `extract_data_strategy` - Data and analytics

### Go-to-Market (4)
- `extract_sales_strategy` - Sales and GTM approach
- `extract_marketing_strategy` - Marketing and brand
- `extract_pricing` - Pricing information
- `extract_pricing_psychology` - Pricing tactics

### Customer & Support (6)
- `extract_onboarding` - Customer success and onboarding
- `extract_support` - Support channels and help
- `extract_reviews` - Customer reviews and ratings
- `extract_content` - Content and learning resources
- `extract_events` - Events and community
- `extract_partners` - Partner program

### Compliance & Risk (6)
- `extract_security` - Security and compliance
- `extract_certifications` - Certifications and standards
- `extract_legal_compliance` - Legal and regulatory
- `extract_sustainability` - ESG and sustainability
- `extract_culture` - Culture and values
- `extract_contact` - Contact information

---

## Usage Examples

### Single Company Enrichment

```bash
# Basic usage
python cli.py enrich URL --schema SCHEMA_NAME --prompt PROMPT_NAME

# With company name
python cli.py enrich https://stripe.com \
  --schema company_profile \
  --prompt extract_company \
  --company "Stripe"

# With custom output
python cli.py enrich https://stripe.com \
  --schema tech_stack \
  --prompt extract_tech_stack \
  --output stripe_tech.json

# With custom variables
python cli.py enrich https://example.com \
  --schema custom \
  --prompt custom_prompt \
  --var industry=SaaS \
  --var focus=AI
```

### Batch Processing

```bash
# Process CSV file
python cli.py batch companies.csv \
  --schema company_profile \
  --prompt extract_company

# Custom column names
python cli.py batch leads.csv \
  --schema icp \
  --prompt extract_icp \
  --url-col website \
  --name-col company_name
```

### Prospect Research (Website + LinkedIn)

```bash
# Website only
python cli.py research "Acme Corp" --website https://acme.com --max-pages 5

# Website + LinkedIn
python cli.py research "Acme Corp" \
  --website https://acme.com \
  --linkedin https://linkedin.com/company/acme

# Export to Google Sheets
python cli.py research "Acme Corp" \
  --website https://acme.com \
  --sheet --sheet-name "Q1 Prospects"
```

### LinkedIn Profile

```bash
python cli.py linkedin-profile "https://linkedin.com/in/john-doe" --output-dir ./output
```

### Example CSV Format (for batch)

```csv
name,url
Stripe,https://stripe.com
Shopify,https://shopify.com
Vercel,https://vercel.com
```

---

## Output Format

### Enrichment output

```json
{
  "company_name": "Stripe",
  "url": "https://stripe.com",
  "schema_used": "company_profile",
  "prompt_used": "extract_company",
  "extracted_data": {
    "company_name": "Stripe",
    "industry": "FinTech",
    "founded_year": 2010,
    "headquarters": "San Francisco, CA",
    "description": "Payment processing platform..."
  },
  "enriched_at": "2025-01-12T15:30:00",
  "model_used": "claude-sonnet-4-20250514"
}
```

### Research output

Research command writes JSON (and optionally Google Sheets) with `ProspectResearch` structure: company name, website data (pages, key points), LinkedIn company data, and LinkedIn posts.

---

## Creating Custom Prompts

1. Create a new file in `prompts/`:

```bash
touch prompts/extract_custom.txt
```

2. Write your prompt with Jinja2 variables:

```text
Extract custom data from {{ company_name }}.

URL: {{ url }}
Content: {{ content }}

Focus on: {{ focus_area }}

Extract specific fields...
```

3. Create a matching schema in `schemas/`:

```json
{
  "name": "custom",
  "description": "Custom data extraction",
  "fields": {
    "field_name": {
      "type": "string",
      "description": "What this field represents",
      "required": true
    }
  }
}
```

4. Run it:

```bash
python cli.py enrich URL \
  --schema custom \
  --prompt extract_custom \
  --var focus_area="security"
```

---

## Directory Structure

```
research-agent/
├── cli.py                 # CLI (enrichment + research)
├── src/
│   ├── config.py          # Configuration
│   ├── models.py          # Data models (EnrichmentResult, ProspectResearch, etc.)
│   ├── scraper.py         # Firecrawl for enrich (single-page)
│   ├── firecrawl_scraper.py # Firecrawl for research (multi-page, key points)
│   ├── extractor.py       # LLM extraction (Claude)
│   ├── linkedin_scraper.py # LinkedIn (Bright Data / Apify)
│   └── google_sheets.py   # Google Sheets export
├── prompts/               # Prompt templates (.txt / .md)
├── schemas/               # Extraction schemas (.json)
├── output/                # Generated outputs
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## Docker Support

```bash
# Build
docker build -t research-agent .

# Run enrichment
docker run -it --rm \
  -v $(pwd)/output:/app/output \
  -e FIRECRAWL_API_KEY=your_key \
  -e ANTHROPIC_API_KEY=your_key \
  research-agent \
  enrich https://stripe.com \
  --schema company_profile \
  --prompt extract_company

# Using docker-compose
docker-compose run research-agent list-schemas
docker-compose run research-agent enrich https://stripe.com --schema company_profile --prompt extract_company
```

---

## Performance & Cost (Enrichment)

- **Speed:** ~5–8 seconds per URL
- **Batch (100):** ~10–15 minutes
- **Cost (approx.):** ~$0.004 per URL
  - Firecrawl: ~$0.001
  - Claude Sonnet: ~$0.003

---

## Use Cases

- **Sales Intelligence** - Enrich prospect lists
- **Competitive Analysis** - Research competitors
- **Market Research** - Analyze market segments
- **Due Diligence** - Investment research
- **Lead Enrichment** - Add data to CRM
- **Prospect Research** - Website + LinkedIn in one run

---

## Troubleshooting

**API Key Errors**
- Ensure required keys are set in `.env` (e.g. `FIRECRAWL_API_KEY`, `ANTHROPIC_API_KEY`)
- Run `python cli.py config-check` to verify

**Schema/Prompt Not Found**
- Check files exist in `prompts/` and `schemas/`
- Use `.txt` or `.md` for prompts, `.json` for schemas
- Schema/prompt name = filename without extension

**Import Errors**
- Run `pip install -r requirements.txt`
- Ensure you are in the `research-agent` directory

---

## License

MIT License

## Support

For issues or questions, check the documentation or create an issue.
