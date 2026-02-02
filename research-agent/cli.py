#!/usr/bin/env python3
"""
Research Agent CLI - Prospect Intelligence Tool

- Enrichment: Extract structured data from websites using prompts and schemas.
- Research: Scrape website data (Firecrawl) and LinkedIn (Bright Data) for prospect research.
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from src.config import settings
from src.models import (
    PromptTemplate,
    ExtractionSchema,
    EnrichmentResult,
    ProspectResearch,
)
from src.scraper import FirecrawlScraper
from src.extractor import LLMExtractor
from src.firecrawl_scraper import FirecrawlScraper as FirecrawlResearchScraper
from src.linkedin_scraper import LinkedInScraper
from src.google_sheets import GoogleSheetsExporter

app = typer.Typer(
    help="Research Agent - Enrichment & Prospect Intelligence Tool"
)
console = Console()


# ---------------------------------------------------------------------------
# Enrichment commands (prompt + schema extraction)
# ---------------------------------------------------------------------------


@app.command()
def list_prompts():
    """List all available prompt templates."""
    prompts_dir = settings.PROMPTS_DIR

    if not prompts_dir.exists():
        console.print(f"[red]Prompts directory not found: {prompts_dir}[/red]")
        return

    prompt_files = list(prompts_dir.glob("*.txt")) + list(prompts_dir.glob("*.md"))

    if not prompt_files:
        console.print("[yellow]No prompt templates found[/yellow]")
        return

    table = Table(title="Available Prompt Templates")
    table.add_column("Name", style="cyan")
    table.add_column("Variables", style="magenta")

    for prompt_file in sorted(prompt_files):
        try:
            template = PromptTemplate.from_file(str(prompt_file))
            table.add_row(
                template.name,
                ", ".join(template.variables) if template.variables else "None",
            )
        except Exception as e:
            console.print(f"[red]Error loading {prompt_file}: {e}[/red]")

    console.print(table)


@app.command()
def list_schemas():
    """List all available extraction schemas."""
    schemas_dir = settings.SCHEMAS_DIR

    if not schemas_dir.exists():
        console.print(f"[red]Schemas directory not found: {schemas_dir}[/red]")
        return

    schema_files = list(schemas_dir.glob("*.json"))

    if not schema_files:
        console.print("[yellow]No extraction schemas found[/yellow]")
        return

    table = Table(title="Available Extraction Schemas")
    table.add_column("Name", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Fields", style="magenta")

    for schema_file in sorted(schema_files):
        try:
            schema = ExtractionSchema.from_file(str(schema_file))
            desc = (
                schema.description[:60] + "..."
                if len(schema.description) > 60
                else schema.description
            )
            table.add_row(schema.name, desc, str(len(schema.fields)))
        except Exception as e:
            console.print(f"[red]Error loading {schema_file}: {e}[/red]")

    console.print(table)


@app.command()
def enrich(
    url: str = typer.Argument(..., help="Website URL to enrich"),
    schema: str = typer.Argument(..., help="Schema name (e.g. company_info)"),
    prompt: str = typer.Argument(..., help="Prompt template name (e.g. company_info)"),
    company_name: Optional[str] = typer.Argument(None, help="Company name (optional)"),
    output_file: Optional[str] = typer.Option(None, "--output", help="Output JSON file path"),
    var: Optional[list[str]] = typer.Option(
        None, "--var", help="Template variables (format: key=value)"
    ),
):
    """Enrich a website URL using a prompt template and extraction schema."""
    # company_name stays as Optional[str]; output_file from Option may need parsing
    template_vars = {}
    if var:
        for v in var:
            if "=" not in v:
                console.print(f"[red]Invalid variable format: {v}. Use key=value[/red]")
                return
            key, value = v.split("=", 1)
            template_vars[key.strip()] = value.strip()

    if company_name:
        template_vars["company_name"] = company_name

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Loading schema...", total=None)
        schema_file = settings.SCHEMAS_DIR / f"{schema}.json"

        if not schema_file.exists():
            console.print(f"[red]Schema not found: {schema_file}[/red]")
            return

        extraction_schema = ExtractionSchema.from_file(str(schema_file))
        progress.update(task, completed=True)
        console.print(f"[green]✓[/green] Loaded schema: {extraction_schema.name}")

        task = progress.add_task("Loading prompt template...", total=None)
        prompt_file = settings.PROMPTS_DIR / f"{prompt}.txt"
        if not prompt_file.exists():
            prompt_file = settings.PROMPTS_DIR / f"{prompt}.md"

        if not prompt_file.exists():
            console.print(f"[red]Prompt template not found: {prompt}[/red]")
            return

        prompt_template = PromptTemplate.from_file(str(prompt_file))
        progress.update(task, completed=True)
        console.print(f"[green]✓[/green] Loaded prompt: {prompt_template.name}")

        task = progress.add_task(f"Scraping {url}...", total=None)
        scraper = FirecrawlScraper()

        try:
            website_content = scraper.scrape_url(url)
            progress.update(task, completed=True)
            console.print(
                f"[green]✓[/green] Scraped website ({len(website_content.markdown)} chars)"
            )
        except Exception as e:
            progress.update(task, completed=True)
            console.print(f"[red]✗[/red] Failed to scrape: {e}")
            return

        task = progress.add_task("Extracting data with Claude...", total=None)
        extractor = LLMExtractor()

        try:
            extracted_data = extractor.extract(
                website_content,
                prompt_template,
                extraction_schema,
                **template_vars,
            )
            progress.update(task, completed=True)
            console.print(f"[green]✓[/green] Extracted {len(extracted_data)} fields")
        except Exception as e:
            progress.update(task, completed=True)
            console.print(f"[red]✗[/red] Failed to extract: {e}")
            return

    result = EnrichmentResult(
        company_name=company_name or url,
        url=url,
        schema_used=extraction_schema.name,
        prompt_used=prompt_template.name,
        extracted_data=extracted_data,
        model_used=settings.ANTHROPIC_MODEL,
    )

    console.print("\n[bold cyan]Extraction Results:[/bold cyan]")
    console.print(json.dumps(extracted_data, indent=2))

    if output_file:
        output_path = Path(output_file)
    else:
        settings.OUTPUT_DIR.mkdir(exist_ok=True)
        timestamp = result.enriched_at.strftime("%Y%m%d_%H%M%S")
        safe_name = "".join(
            c
            for c in (company_name or "enrichment")
            if c.isalnum() or c in (" ", "-", "_")
        ).strip()
        safe_name = safe_name.replace(" ", "_")
        output_path = settings.OUTPUT_DIR / f"{safe_name}_{timestamp}.json"

    with open(output_path, "w") as f:
        json.dump(result.to_json(), f, indent=2)

    console.print(f"\n[green]✓[/green] Saved to: {output_path}")


@app.command()
def batch(
    input_file: str = typer.Argument(..., help="CSV file with URLs"),
    schema: str = typer.Option(..., "--schema", "-s", help="Schema name"),
    prompt: str = typer.Option(..., "--prompt", "-p", help="Prompt template name"),
    url_column: str = typer.Option("url", "--url-col", help="Column name for URLs"),
    name_column: str = typer.Option(
        "name", "--name-col", help="Column name for company names"
    ),
):
    """Batch enrich multiple URLs from a CSV file."""
    import csv

    input_path = Path(input_file)

    if not input_path.exists():
        console.print(f"[red]Input file not found: {input_file}[/red]")
        return

    urls_data = []
    with open(input_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            urls_data.append({
                "name": row.get(name_column, ""),
                "url": row.get(url_column, ""),
            })

    console.print(f"[cyan]Processing {len(urls_data)} URLs...[/cyan]\n")

    schema_file = settings.SCHEMAS_DIR / f"{schema}.json"
    extraction_schema = ExtractionSchema.from_file(str(schema_file))

    prompt_file = settings.PROMPTS_DIR / f"{prompt}.txt"
    if not prompt_file.exists():
        prompt_file = settings.PROMPTS_DIR / f"{prompt}.md"
    prompt_template = PromptTemplate.from_file(str(prompt_file))

    scraper = FirecrawlScraper()
    extractor = LLMExtractor()

    results = []
    for idx, item in enumerate(urls_data, 1):
        url = item.get("url", "")
        name = item.get("name", url)

        console.print(f"[{idx}/{len(urls_data)}] Processing: {name}")

        try:
            website_content = scraper.scrape_url(url)
            extracted_data = extractor.extract(
                website_content,
                prompt_template,
                extraction_schema,
                company_name=name,
            )

            result = EnrichmentResult(
                company_name=name,
                url=url,
                schema_used=extraction_schema.name,
                prompt_used=prompt_template.name,
                extracted_data=extracted_data,
                model_used=settings.ANTHROPIC_MODEL,
            )

            results.append(result)
            console.print("  [green]✓[/green] Success\n")

        except Exception as e:
            console.print(f"  [red]✗[/red] Error: {e}\n")
            continue

    settings.OUTPUT_DIR.mkdir(exist_ok=True)
    timestamp = (
        results[0].enriched_at.strftime("%Y%m%d_%H%M%S") if results else "empty"
    )
    output_path = settings.OUTPUT_DIR / f"batch_{timestamp}.json"

    with open(output_path, "w") as f:
        json.dump([r.to_json() for r in results], f, indent=2)

    console.print(f"\n[green]✓[/green] Processed {len(results)}/{len(urls_data)} successfully")
    console.print(f"[green]✓[/green] Saved to: {output_path}")


# ---------------------------------------------------------------------------
# Prospect research commands (website + LinkedIn)
# ---------------------------------------------------------------------------


@app.command()
def research(
    company_name: str = typer.Argument(..., help="Company name to research"),
    website: Optional[str] = typer.Option(
        None, "--website", "-w", help="Company website URL"
    ),
    linkedin_url: Optional[str] = typer.Option(
        None, "--linkedin", "-l", help="LinkedIn company URL"
    ),
    max_pages: int = typer.Option(
        5, "--max-pages", "-m", help="Maximum pages to scrape per website"
    ),
    output_json: bool = typer.Option(True, "--json", help="Save JSON output"),
    output_sheet: bool = typer.Option(False, "--sheet", help="Export to Google Sheets"),
    sheet_name: Optional[str] = typer.Option(
        None, "--sheet-name", help="Google Sheet name (if exporting)"
    ),
    output_dir: str = typer.Option("./output", "--output-dir", "-o", help="Output directory"),
):
    """
    Research a company/prospect using website scraping and LinkedIn data.

    Examples:
        research-agent research "Acme Corp" --website https://acme.com --max-pages 5
        research-agent research "Acme Corp" --website https://acme.com --linkedin https://linkedin.com/company/acme
        research-agent research "Acme Corp" --website https://acme.com --sheet --sheet-name "Q1 Prospects"
    """
    console.print(
        f"\n[bold cyan]🔍 Starting research for:[/bold cyan] {company_name}\n"
    )

    asyncio.run(
        _research_async(
            company_name,
            website,
            linkedin_url,
            max_pages,
            output_json,
            output_sheet,
            sheet_name,
            Path(output_dir),
        )
    )


async def _research_async(
    company_name: str,
    website: Optional[str],
    linkedin_url: Optional[str],
    max_pages: int,
    output_json: bool,
    output_sheet: bool,
    sheet_name: Optional[str],
    output_dir: Path,
):
    """Async research operation."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        research_data = ProspectResearch(
            company_name=company_name,
            website_url=website,
            linkedin_url=linkedin_url,
            timestamp=datetime.now(),
        )

        if website:
            task = progress.add_task(
                f"Scraping website (max {max_pages} pages)...", total=None
            )
            try:
                scraper = FirecrawlResearchScraper()
                website_data = scraper.scrape_website(website, max_pages=max_pages)
                research_data.website_data = website_data
                progress.update(task, completed=True)
                console.print(
                    f"[green]✓[/green] Scraped {len(website_data.pages_scraped)} pages"
                )
                console.print(
                    f"[green]✓[/green] Extracted {len(website_data.key_points)} key points"
                )
            except Exception as e:
                progress.update(task, completed=True)
                console.print(f"[yellow]⚠[/yellow] Website scraping failed: {e}")

        if linkedin_url:
            task = progress.add_task(
                "Fetching LinkedIn company data...", total=None
            )
            try:
                linkedin = LinkedInScraper()
                company_data = await linkedin.scrape_company(linkedin_url)
                research_data.linkedin_company_data = company_data
                progress.update(task, completed=True)
                console.print(
                    f"[green]✓[/green] LinkedIn company data fetched (source: {company_data.source})"
                )
            except Exception as e:
                progress.update(task, completed=True)
                console.print(f"[yellow]⚠[/yellow] LinkedIn scraping failed: {e}")

            task = progress.add_task("Fetching LinkedIn posts...", total=None)
            try:
                posts = await linkedin.get_company_posts(linkedin_url, limit=10)
                research_data.linkedin_posts = posts
                progress.update(task, completed=True)
                if posts:
                    console.print(
                        f"[green]✓[/green] Fetched {len(posts)} LinkedIn posts (source: {posts[0].source})"
                    )
                else:
                    console.print("[yellow]⚠[/yellow] No LinkedIn posts found")
            except Exception as e:
                progress.update(task, completed=True)
                console.print("[yellow]⚠[/yellow] Failed to fetch posts: {e}")

    console.print("\n[bold cyan]💾 Saving results...[/bold cyan]\n")

    output_dir.mkdir(parents=True, exist_ok=True)

    if output_json:
        json_file = output_dir / (
            f"{company_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(json_file, "w") as f:
            json.dump(research_data.model_dump(), f, indent=2, default=str)
        console.print(f"[green]✓[/green] JSON saved: {json_file}")

    if output_sheet:
        try:
            exporter = GoogleSheetsExporter()
            sheet_url = exporter.export_research(research_data, sheet_name)
            console.print(f"[green]✓[/green] Google Sheet created: {sheet_url}")
        except Exception as e:
            console.print(
                f"[red]✗[/red] Failed to export to Google Sheets: {e}"
            )

    console.print("\n[bold green]✅ Research completed![/bold green]\n")


@app.command()
def linkedin_profile(
    profile_url: str = typer.Argument(..., help="LinkedIn profile URL"),
    output_json: bool = typer.Option(True, "--json", help="Save JSON output"),
    output_dir: str = typer.Option("./output", "--output-dir", "-o", help="Output directory"),
):
    """
    Research an individual LinkedIn profile.

    Example:
        research-agent linkedin-profile "https://linkedin.com/in/john-doe"
    """
    console.print(
        f"\n[bold cyan]🔍 Fetching LinkedIn profile:[/bold cyan] {profile_url}\n"
    )

    async def _fetch():
        linkedin = LinkedInScraper()
        return await linkedin.scrape_profile(profile_url)

    try:
        profile_data = asyncio.run(_fetch())

        console.print("[green]✓[/green] Profile data fetched successfully\n")

        if output_json:
            out_path = Path(output_dir)
            out_path.mkdir(parents=True, exist_ok=True)
            json_file = out_path / (
                f"linkedin_profile_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            with open(json_file, "w") as f:
                json.dump(profile_data, f, indent=2, default=str)
            console.print(f"[green]✓[/green] JSON saved: {json_file}")

        console.print("\n[bold green]✅ Complete![/bold green]\n")

    except Exception as e:
        console.print(f"[red]✗[/red] Error: {e}")
        sys.exit(1)


@app.command()
def config_check():
    """Check configuration and API credentials."""
    console.print("\n[bold cyan]⚙️  Configuration Check[/bold cyan]\n")

    checks = {
        "Firecrawl API Key": bool(settings.FIRECRAWL_API_KEY),
        "Bright Data API Key": bool(settings.BRIGHTDATA_API_KEY),
        "Google Sheets Credentials": (
            settings.GOOGLE_CREDENTIALS_PATH.exists()
            if settings.GOOGLE_CREDENTIALS_PATH
            else False
        ),
    }

    for name, status in checks.items():
        icon = "✓" if status else "✗"
        color = "green" if status else "red"
        console.print(f"[{color}]{icon}[/{color}] {name}")

    console.print()


if __name__ == "__main__":
    app()
