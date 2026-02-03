#!/usr/bin/env python3
"""Test script for verifying Research Agent feature implementations."""

import sys
import os
import json
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)


def _run_cli(args):
    return subprocess.run(
        [sys.executable, "cli.py", *args],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
        env={
            **os.environ,
            "PYTHONPATH": str(PROJECT_ROOT),
        },
    )

def test_cli_structure():
    """Test Feature 1: CLI Interface"""
    print("=" * 60)
    print("FEATURE 1: CLI Interface for Research Agent")
    print("=" * 60)
    
    try:
        from src.config import settings
        print("✓ Config imports successfully")
        print(f"  - Firecrawl URL: {settings.FIRECRAWL_API_URL}")
        print(f"  - Prompts dir: {settings.PROMPTS_DIR}")
        print(f"  - Schemas dir: {settings.SCHEMAS_DIR}")
        print(f"  - Output dir: {settings.OUTPUT_DIR}")
    except Exception as e:
        print(f"✗ Config import failed: {e}")
        return False
    
    try:
        from src.models import PromptTemplate, ExtractionSchema
        print("✓ Models import successfully")
    except Exception as e:
        print(f"✗ Models import failed: {e}")
        return False
    
    # Check prompts exist
    prompts = list(settings.PROMPTS_DIR.glob("*.txt")) + list(
        settings.PROMPTS_DIR.glob("*.md")
    )
    print(f"✓ Found {len(prompts)} prompt templates")
    for p in prompts:
        print(f"  - {p.name}")
    
    # Check schemas exist
    schemas = list(settings.SCHEMAS_DIR.glob("*.json"))
    print(f"✓ Found {len(schemas)} extraction schemas")
    for s in schemas:
        print(f"  - {s.name}")

    # Validate CLI commands available (from README) without invoking --help
    try:
        import cli as cli_module

        command_names = []
        for cmd in cli_module.app.registered_commands:
            name = cmd.name or cmd.callback.__name__.replace("_", "-")
            command_names.append(name)
    except Exception as e:
        print(f"✗ CLI command inspection failed: {e}")
        return False

    expected_commands = [
        "list-prompts",
        "list-schemas",
        "enrich",
        "batch",
        "research",
        "linkedin-profile",
        "config-check",
    ]
    missing = [cmd for cmd in expected_commands if cmd not in command_names]
    if missing:
        print(f"✗ Missing CLI commands: {', '.join(missing)}")
        return False
    print("✓ CLI commands available")
    
    print()
    return True


def test_scraper_structure():
    """Test Feature 2: Website Scraping via Firecrawl API"""
    print("=" * 60)
    print("FEATURE 2: Website Scraping via Firecrawl API")
    print("=" * 60)
    
    try:
        from src.scraper import FirecrawlScraper
        from src.firecrawl_scraper import FirecrawlScraper as FirecrawlResearchScraper
        from src.linkedin_scraper import LinkedInScraper
        from src.models import WebsiteContent, WebsiteData
        print("✓ Scraper imports successfully")
        print("✓ FirecrawlScraper class available")
        print("✓ FirecrawlResearchScraper class available")
        print("✓ LinkedInScraper class available")
        print("✓ WebsiteContent model available")
        print("✓ WebsiteData model available")
        
        # Check methods
        scraper_methods = [m for m in dir(FirecrawlScraper) if not m.startswith('_')]
        print(f"✓ Scraper methods: {', '.join(scraper_methods)}")
        
    except Exception as e:
        print(f"✗ Scraper import failed: {e}")
        return False
    
    print()
    return True


def test_extractor_structure():
    """Test Feature 3: LLM Data Extraction with Schema Validation"""
    print("=" * 60)
    print("FEATURE 3: LLM Data Extraction with Schema Validation")
    print("=" * 60)
    
    try:
        from src.extractor import LLMExtractor
        from src.models import EnrichmentResult
        print("✓ Extractor imports successfully")
        print("✓ LLMExtractor class available")
        print("✓ EnrichmentResult model available")
        
        # Test schema loading
        from src.models import ExtractionSchema
        schema_file = PROJECT_ROOT / "schemas" / "company_info.json"
        if schema_file.exists():
            schema = ExtractionSchema.from_file(str(schema_file))
            print(f"✓ Schema loading works: {schema.name}")
            print(f"  - Fields: {', '.join(schema.fields.keys())}")
        
        # Test prompt loading
        from src.models import PromptTemplate
        prompt_file = PROJECT_ROOT / "prompts" / "company_info.txt"
        if prompt_file.exists():
            template = PromptTemplate.from_file(str(prompt_file))
            print(f"✓ Template loading works: {template.name}")
            print(f"  - Variables: {', '.join(template.variables)}")
            
    except Exception as e:
        print(f"✗ Extractor test failed: {e}")
        return False
    
    print()
    return True


def test_batch_processing():
    """Test Feature 5: Batch Processing for Multiple URLs"""
    print("=" * 60)
    print("FEATURE 5: Batch Processing for Multiple URLs")
    print("=" * 60)
    
    try:
        # Check if sample CSV exists
        csv_file = PROJECT_ROOT / "sample_batch.csv"
        if csv_file.exists():
            print("✓ Sample batch CSV exists")
            with open(csv_file) as f:
                content = f.read()
                lines = content.strip().split('\n')
                print(f"  - {len(lines)} lines (including header)")
                print(f"  - First line: {lines[0]}")
        else:
            print("✗ Sample batch CSV not found")
            return False
        
        # Check batch command is registered (avoid running networked job)
        import cli as cli_module
        batch_registered = any(
            (cmd.name or cmd.callback.__name__.replace("_", "-")) == "batch"
            for cmd in cli_module.app.registered_commands
        )
        if batch_registered:
            print("✓ CLI batch command available")
        else:
            print("✗ CLI batch command not registered")
            return False
            
    except Exception as e:
        print(f"✗ Batch processing test failed: {e}")
        return False
    
    print()
    return True


def test_readme_commands():
    """Test README quick-start CLI commands (safe checks)."""
    print("=" * 60)
    print("README: Quick Start Commands")
    print("=" * 60)

    commands = [
        (["list-prompts"], "Available Prompt Templates"),
        (["list-schemas"], "Available Extraction Schemas"),
        (["config-check"], "Configuration Check"),
    ]

    for args, expected in commands:
        result = _run_cli(args)
        if result.returncode != 0:
            print(f"✗ Command failed: {' '.join(args)}")
            print(result.stderr)
            return False
        if expected not in result.stdout:
            print(f"✗ Expected output not found for: {' '.join(args)}")
            return False
        print(f"✓ {' '.join(args)} works")

    print()
    return True


def test_cli_functions_registered():
    """Validate all CLI functions are defined and registered (no network calls)."""
    print("=" * 60)
    print("CLI: Command Functions Registered")
    print("=" * 60)

    try:
        import inspect
        import cli as cli_module

        expected = {
            "list-prompts": "list_prompts",
            "list-schemas": "list_schemas",
            "enrich": "enrich",
            "batch": "batch",
            "research": "research",
            "linkedin-profile": "linkedin_profile",
            "config-check": "config_check",
        }

        command_map = {}
        for cmd in cli_module.app.registered_commands:
            name = cmd.name or cmd.callback.__name__.replace("_", "-")
            command_map[name] = cmd.callback

        missing = [k for k in expected if k not in command_map]
        if missing:
            print(f"✗ Missing CLI commands: {', '.join(missing)}")
            return False

        extra = [k for k in command_map if k not in expected]
        if extra:
            print(f"✗ Unexpected CLI commands: {', '.join(extra)}")
            return False

        for cmd_name, func_name in expected.items():
            func = getattr(cli_module, func_name, None)
            if func is None:
                print(f"✗ Missing function: {func_name}")
                return False
            if command_map[cmd_name] is not func:
                print(f"✗ Command '{cmd_name}' not bound to {func_name}")
                return False

        # Signature sanity checks (avoid executing network code)
        signatures = {
            "enrich": ["url", "schema", "prompt"],
            "batch": ["input_file", "schema", "prompt"],
            "research": ["company_name"],
            "linkedin_profile": ["profile_url"],
        }

        for func_name, params in signatures.items():
            sig = inspect.signature(getattr(cli_module, func_name))
            missing_params = [p for p in params if p not in sig.parameters]
            if missing_params:
                print(
                    f"✗ {func_name} missing params: {', '.join(missing_params)}"
                )
                return False

        print("✓ All CLI functions registered and validated")
        print()
        return True

    except Exception as e:
        print(f"✗ CLI function registration test failed: {e}")
        return False


def main():
    """Run all Research Agent feature tests."""
    print("\n" + "=" * 60)
    print("RESEARCH AGENT FEATURE VERIFICATION TEST SUITE")
    print("=" * 60)
    print()
    
    results = []
    
    # Test Research Agent features only (Email Notifier has its own tests in email-open-discord-notifier/)
    results.append(("Feature 1: CLI Interface", test_cli_structure()))
    results.append(("Feature 2: Website Scraping", test_scraper_structure()))
    results.append(("Feature 3: LLM Extraction", test_extractor_structure()))
    results.append(("Feature 5: Batch Processing", test_batch_processing()))
    results.append(("README: Quick Start", test_readme_commands()))
    results.append(("CLI: Functions Registered", test_cli_functions_registered()))
    
    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    print()
    print(f"Total: {passed}/{total} features verified")
    print("=" * 60)
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
