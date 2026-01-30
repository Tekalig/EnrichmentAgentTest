# Research Agent

Automated prospect research tool combining website scraping and LinkedIn intelligence.

## Features

- 🌐 Website scraping via Firecrawl API
- 🤖 LLM-powered data extraction using Claude
- 📊 Structured data extraction with JSON schemas
- 📝 Custom prompt templates
- 💾 JSON output for further processing
- 🐳 Docker containerized

## Quick Start

### Local Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
# Edit .env with your API keys

# List available schemas
python cli.py list-schemas

# List available prompts
python cli.py list-prompts

# Enrich a single URL
python cli.py enrich https://example.com \
  --schema company_info \
  --prompt company_info \
  --company "Example Corp"

# Batch process multiple URLs
python cli.py batch companies.csv \
  --schema company_info \
  --prompt company_info
```

### Docker

```bash
# Build
docker-compose build

# Run
docker-compose run research-agent list-schemas

# Enrich with Docker
docker-compose run research-agent enrich https://example.com \
  --schema company_info \
  --prompt company_info
```

## Configuration

Required environment variables:
- `FIRECRAWL_API_KEY` - Get from https://firecrawl.dev
- `ANTHROPIC_API_KEY` - Get from https://anthropic.com

Optional:
- `BRIGHTDATA_API_KEY` - For LinkedIn data
- `GOOGLE_CREDENTIALS_PATH` - For Google Sheets export

## CLI Commands

### list-schemas
List all available extraction schemas.

```bash
python cli.py list-schemas
```

### list-prompts
List all available prompt templates.

```bash
python cli.py list-prompts
```

### enrich
Enrich a single URL with specified schema and prompt.

```bash
python cli.py enrich URL \
  --schema SCHEMA_NAME \
  --prompt PROMPT_NAME \
  --company "Company Name" \
  --output output.json
```

### batch
Batch process multiple URLs from a CSV file.

```bash
python cli.py batch input.csv \
  --schema SCHEMA_NAME \
  --prompt PROMPT_NAME \
  --url-col url \
  --name-col name
```

## Directory Structure

```
research-agent/
├── cli.py              # CLI application
├── src/
│   ├── config.py       # Configuration
│   ├── models.py       # Data models
│   ├── scraper.py      # Firecrawl integration
│   ├── extractor.py    # LLM extraction
│   ├── firecrawl_scraper.py  # Advanced scraping
│   ├── linkedin_scraper.py   # LinkedIn integration
│   └── google_sheets.py      # Sheets export
├── prompts/            # Prompt templates
├── schemas/            # Extraction schemas
├── output/             # Generated outputs
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Creating Custom Prompts

Create a new file in `prompts/` directory:

```text
Extract information about {{ company_name }} from the following content:

URL: {{ url }}

Content:
{{ content }}

Focus on extracting the specified fields accurately.
```

## Creating Custom Schemas

Create a new JSON file in `schemas/` directory:

```json
{
  "name": "my_schema",
  "description": "Custom extraction schema",
  "fields": {
    "field1": {
      "type": "string",
      "description": "Field description",
      "required": true
    },
    "field2": {
      "type": "array",
      "description": "List of items",
      "required": false,
      "default": []
    }
  }
}
```

## Output Format

Enrichment results are saved as JSON:

```json
{
  "company_name": "Example Corp",
  "url": "https://example.com",
  "schema_used": "company_info",
  "prompt_used": "company_info",
  "extracted_data": {
    "company_name": "Example Corp",
    "industry": "Technology",
    "description": "...",
    ...
  },
  "enriched_at": "2024-01-30T12:00:00",
  "model_used": "claude-sonnet-4"
}
```

## Troubleshooting

**API Key Errors:**
- Ensure all required API keys are set in `.env`
- Check API key validity at provider dashboards

**Import Errors:**
- Run `pip install -r requirements.txt`
- Ensure you're in the correct directory

**Schema/Prompt Not Found:**
- Check files exist in `prompts/` and `schemas/` directories
- Verify file extensions (.txt for prompts, .json for schemas)

## License

MIT License - See LICENSE file for details
