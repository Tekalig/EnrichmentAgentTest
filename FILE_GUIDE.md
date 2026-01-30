# Repository File Guide

This document explains the file structure of the repository after restructuring.

## Active Services (Use These)

### 1. Research Agent
**Location:** `research-agent/`  
**Entry Point:** `research-agent/cli.py`  
**Documentation:** `research-agent/README.md`

### 2. Email Open Discord Notifier
**Location:** `email-open-discord-notifier/`  
**Entry Point:** `email-open-discord-notifier/main.py`  
**Documentation:** `email-open-discord-notifier/README.md`

## Root Level Files

### Active Files
- `README.md` - Main repository overview, points to services
- `RESTRUCTURING.md` - Migration guide from old to new structure
- `.gitignore` - Version control configuration

### Legacy Files (Historical)
These files remain from the previous flat structure for reference:

**Old Application Files:**
- `cli.py` - Old CLI (now at `research-agent/cli.py`)
- `main.py` - Old FastAPI app (now at `email-open-discord-notifier/main.py`)
- `src/` - Old shared modules (now split between services)

**Old Configuration Files:**
- `config (1).py` - Old research agent config
- `config (2).py` - Old email notifier config
- `__init__ (1).py` - Old research agent init
- `__init__ (2).py` - Old email notifier init
- `models (1).py` - Old research agent models
- `models (2).py` - Old email notifier models

**Old Support Files:**
- `prompts/` - Moved to `research-agent/prompts/`
- `schemas/` - Moved to `research-agent/schemas/`
- `firecrawl_scraper.py` - Moved to `research-agent/src/`
- `linkedin_scraper.py` - Moved to `research-agent/src/`
- `google_sheets.py` - Moved to `research-agent/src/`
- `companies.csv` - Sample data
- `sample_batch.csv` - Sample batch input

**Old Documentation:**
- `FEATURE_VERIFICATION_REPORT.md` - Previous verification report
- `TASK_COMPLETION_SUMMARY.md` - Previous task summary
- `BRANCH_README.md` - Previous branch documentation
- `IMPLEMENTATION_SUMMARY.md` - Old implementation docs
- `ANALYTICS.md`, `CHANGES.md`, etc. - Historical documentation

**Old Docker Files:**
- `Dockerfile` - Old unified dockerfile
- `docker-compose.yml` - Old unified compose file
- `Dockerfile (1)`, `docker-compose (1).yml` - Duplicates

**Old Requirements:**
- `requirements.txt` - Old unified requirements
- `requirements (1).txt`, `requirements (2).txt` - Duplicates

**Old README Versions:**
- `README (1).md`, `README (2).md`, `README (3).md` - Old versions

### Data Directories
- `Extract_Texts/` - Text extraction samples
- `JSON_DATA/` - JSON data samples

## What To Use

### For Research Agent (Prospect Research)
```bash
cd research-agent/
python cli.py --help
```
See `research-agent/README.md` for full documentation.

### For Email Notifier (Email Tracking)
```bash
cd email-open-discord-notifier/
python main.py
```
See `email-open-discord-notifier/README.md` for full documentation.

## Migration

If you were using files from the root level:

**Old Way:**
```bash
python cli.py list-schemas
python main.py
```

**New Way:**
```bash
cd research-agent && python cli.py list-schemas
cd email-open-discord-notifier && python main.py
```

## Cleanup Recommendations

To clean up the repository, you may want to:

1. **Archive legacy files** to a `legacy/` directory
2. **Remove duplicate files** (files with numbers in names)
3. **Keep historical docs** in a `docs/archive/` directory
4. **Remove old Docker files** at root level
5. **Remove old src/** directory** at root level

Example cleanup:
```bash
# Create archive directories
mkdir -p legacy docs/archive

# Move old files
mv cli.py main.py legacy/
mv src/ legacy/
mv "config (1).py" "config (2).py" legacy/
mv *.md docs/archive/  # Except README.md and RESTRUCTURING.md

# Remove duplicates
rm "Dockerfile (1)" "docker-compose (1).yml"
rm "requirements (1).txt" "requirements (2).txt"
rm "README (1).md" "README (2).md" "README (3).md"
```

## Summary

- ✅ **Use:** `research-agent/` and `email-open-discord-notifier/` directories
- ⚠️ **Legacy:** Root level Python files and old configs
- 📁 **Archive:** Old documentation and duplicate files
- 📚 **Docs:** Each service has its own comprehensive README

For the latest information, always refer to:
- `research-agent/README.md`
- `email-open-discord-notifier/README.md`
- `RESTRUCTURING.md`
