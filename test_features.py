#!/usr/bin/env python3
"""Test script for verifying feature implementations"""

import sys
import json
from pathlib import Path

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
    prompts = list(settings.PROMPTS_DIR.glob("*.txt")) + list(settings.PROMPTS_DIR.glob("*.md"))
    print(f"✓ Found {len(prompts)} prompt templates")
    for p in prompts:
        print(f"  - {p.name}")
    
    # Check schemas exist
    schemas = list(settings.SCHEMAS_DIR.glob("*.json"))
    print(f"✓ Found {len(schemas)} extraction schemas")
    for s in schemas:
        print(f"  - {s.name}")
    
    print()
    return True


def test_scraper_structure():
    """Test Feature 2: Website Scraping via Firecrawl API"""
    print("=" * 60)
    print("FEATURE 2: Website Scraping via Firecrawl API")
    print("=" * 60)
    
    try:
        from src.scraper import FirecrawlScraper
        from src.models import WebsiteContent
        print("✓ Scraper imports successfully")
        print("✓ FirecrawlScraper class available")
        print("✓ WebsiteContent model available")
        
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
        schema_file = Path("schemas/company_info.json")
        if schema_file.exists():
            schema = ExtractionSchema.from_file(str(schema_file))
            print(f"✓ Schema loading works: {schema.name}")
            print(f"  - Fields: {', '.join(schema.fields.keys())}")
        
        # Test prompt loading
        from src.models import PromptTemplate
        prompt_file = Path("prompts/company_info.txt")
        if prompt_file.exists():
            template = PromptTemplate.from_file(str(prompt_file))
            print(f"✓ Template loading works: {template.name}")
            print(f"  - Variables: {', '.join(template.variables)}")
            
    except Exception as e:
        print(f"✗ Extractor test failed: {e}")
        return False
    
    print()
    return True


def test_email_notifier_structure():
    """Test Feature 4: Email Open Discord Notifier"""
    print("=" * 60)
    print("FEATURE 4: Email Open Discord Notifier (FastAPI Service)")
    print("=" * 60)
    
    try:
        # Check if main.py exists
        import main
        print("✓ main.py module available")
        print("✓ FastAPI app defined")
        
        # Check for key endpoints
        app = main.app
        routes = [route.path for route in app.routes]
        print(f"✓ Found {len(routes)} routes:")
        for route in routes[:10]:  # Show first 10
            print(f"  - {route}")
            
    except Exception as e:
        print(f"✗ Email notifier test failed: {e}")
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
        csv_file = Path("sample_batch.csv")
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
        
        # Test CLI batch command directly
        import subprocess
        result = subprocess.run(
            ["python3", "cli.py", "batch", "--help"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0 and "Batch enrich" in result.stdout:
            print("✓ CLI batch command available")
            print("✓ Batch command help works")
        else:
            print("✗ Batch command not working properly")
            return False
            
    except Exception as e:
        print(f"✗ Batch processing test failed: {e}")
        return False
    
    print()
    return True


def main():
    """Run all feature tests"""
    print("\n" + "=" * 60)
    print("FEATURE VERIFICATION TEST SUITE")
    print("=" * 60)
    print()
    
    results = []
    
    # Test each feature
    results.append(("Feature 1: CLI Interface", test_cli_structure()))
    results.append(("Feature 2: Website Scraping", test_scraper_structure()))
    results.append(("Feature 3: LLM Extraction", test_extractor_structure()))
    results.append(("Feature 4: Email Notifier", test_email_notifier_structure()))
    results.append(("Feature 5: Batch Processing", test_batch_processing()))
    
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
