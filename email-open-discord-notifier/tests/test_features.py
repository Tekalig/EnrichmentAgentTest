#!/usr/bin/env python3
"""Test script for verifying Email Open Discord Notifier features."""

import os
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from contextlib import asynccontextmanager

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
	sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)


def _route_methods(app):
	routes = {}
	for route in app.router.routes:
		methods = getattr(route, "methods", None)
		path = getattr(route, "path", None)
		if methods and path:
			routes[path] = {m.upper() for m in methods}
	return routes


def test_app_structure():
	"""Verify FastAPI app and core models/config import."""
	print("=" * 60)
	print("FEATURE 1: FastAPI App Structure")
	print("=" * 60)

	try:
		import main
		from src.config import settings
		from src.models import EmailOpenEvent

		print("✓ main.py imports successfully")
		print("✓ Settings available")
		print("✓ EmailOpenEvent model available")

		app = main.app
		print(f"✓ App title: {app.title}")
		print(f"✓ App version: {app.version}")
	except Exception as e:
		print(f"✗ App structure test failed: {e}")
		return False

	print()
	return True


def test_routes_registered():
	"""Verify all documented routes exist without running the server."""
	print("=" * 60)
	print("FEATURE 2: API Routes Registered")
	print("=" * 60)

	try:
		import main

		routes = _route_methods(main.app)
		expected = {
			"/": {"GET"},
			"/health": {"GET"},
			"/webhook/closeio": {"POST"},
			"/stats": {"GET"},
			"/test/notification": {"POST"},
			"/analytics/summary": {"GET"},
			"/analytics/recent": {"GET"},
			"/analytics/by-date": {"GET"},
			"/analytics/by-lead/{lead_id}": {"GET"},
			"/analytics/top-leads": {"GET"},
			"/analytics/time-of-day": {"GET"},
			"/analytics/day-of-week": {"GET"},
			"/analytics/engagement": {"GET"},
		}

		missing = []
		for path, methods in expected.items():
			if path not in routes:
				missing.append(f"{path} ({', '.join(methods)})")
				continue
			if not methods.issubset(routes[path]):
				missing.append(f"{path} ({', '.join(methods)})")

		if missing:
			print("✗ Missing routes:")
			for item in missing:
				print(f"  - {item}")
			return False

		print("✓ All documented routes are registered")
	except Exception as e:
		print(f"✗ Routes test failed: {e}")
		return False

	print()
	return True


def test_readme_documentation():
	"""Verify README references key run and API usage instructions."""
	print("=" * 60)
	print("FEATURE 3: README Documentation")
	print("=" * 60)

	readme_path = PROJECT_ROOT / "README.md"
	if not readme_path.exists():
		print("✗ README.md not found")
		return False

	content = readme_path.read_text()
	required_snippets = [
		"uvicorn main:app",
		"python main.py",
		"curl http://localhost:8000/health",
		"POST http://localhost:8000/webhook/closeio",
		"curl http://localhost:8000/analytics/summary",
		"curl -X POST http://localhost:8000/test/notification",
		"docker-compose up -d",
	]

	missing = [s for s in required_snippets if s not in content]
	if missing:
		print("✗ README missing expected snippets:")
		for item in missing:
			print(f"  - {item}")
		return False

	print("✓ README contains key run and API instructions")
	print()
	return True


def test_endpoints_response():
	"""Hit lightweight endpoints via ASGI transport (lifespan off)."""
	print("=" * 60)
	print("FEATURE 4: Endpoint Responses")
	print("=" * 60)

	try:
		import main

		@dataclass
		class DummyOpen:
			email_id: str
			lead_id: str
			lead_name: str
			subject: str
			recipient: str
			opens_count: int
			opened_at: datetime
			notified_at: datetime
			date_opened: str

		dummy_open = DummyOpen(
			email_id="email_1",
			lead_id="lead_1",
			lead_name="Test Lead",
			subject="Hello",
			recipient="test@example.com",
			opens_count=1,
			opened_at=datetime(2025, 1, 1, 12, 0, 0),
			notified_at=datetime(2025, 1, 1, 12, 5, 0),
			date_opened="2025-01-01",
		)

		async def _fake_summary():
			return {"total_opens": 1, "unique_emails": 1, "unique_leads": 1}

		async def _fake_recent(limit: int = 50):
			return [dummy_open]

		async def _fake_by_date(start_date: str, end_date: str):
			return [dummy_open]

		async def _fake_by_lead(lead_id: str):
			return [dummy_open] if lead_id == "lead_1" else []

		async def _fake_top_leads(limit: int = 10):
			return [{"lead_id": "lead_1", "lead_name": "Test Lead", "total_opens": 1}]

		async def _fake_time_of_day():
			return [{"hour": 9, "opens_count": 1, "unique_leads": 1}]

		async def _fake_day_of_week():
			return [{"day_of_week": 0, "day_name": "Monday", "opens_count": 1, "unique_leads": 1}]

		async def _fake_engagement(days: int = 30):
			return {
				"period_days": days,
				"total_opens": 1,
				"unique_emails": 1,
				"unique_leads": 1,
				"avg_opens_per_email": 1.0,
				"max_opens_per_email": 1,
			}

		class DummyCache:
			async def get_stats(self):
				return {"total_count": 1, "cache_size": 1, "oldest_entry": "2025-01-01T00:00:00"}

		class DummyDiscord:
			async def send_email_open_notification(self, event):
				return None

		main.get_analytics_summary = _fake_summary
		main.get_recent_opens = _fake_recent
		main.get_opens_by_date = _fake_by_date
		main.get_opens_by_lead = _fake_by_lead
		main.get_top_leads = _fake_top_leads
		main.get_opens_by_time_of_day = _fake_time_of_day
		main.get_opens_by_day_of_week = _fake_day_of_week
		main.get_engagement_metrics = _fake_engagement

		@asynccontextmanager
		async def _noop_lifespan(app):
			app.state.cache = DummyCache()
			app.state.discord = DummyDiscord()
			yield

		main.app.router.lifespan_context = _noop_lifespan

		with TestClient(main.app) as client:
			root_response = client.get("/")
			if root_response.status_code != 200:
				print(f"✗ / returned {root_response.status_code}")
				return False

			root_json = root_response.json()
			if "service" not in root_json or "status" not in root_json:
				print("✗ / response missing expected keys")
				return False

			health_response = client.get("/health")
			if health_response.status_code != 200:
				print(f"✗ /health returned {health_response.status_code}")
				return False

			health_json = health_response.json()
			if "status" not in health_json or "timestamp" not in health_json:
				print("✗ /health response missing expected keys")
				return False

			if client.get("/stats").status_code != 200:
				print("✗ /stats returned non-200")
				return False

			if client.post("/test/notification").status_code != 200:
				print("✗ /test/notification returned non-200")
				return False

			if client.get("/analytics/summary").status_code != 200:
				print("✗ /analytics/summary returned non-200")
				return False

			if client.get("/analytics/recent?limit=10").status_code != 200:
				print("✗ /analytics/recent returned non-200")
				return False

			if client.get("/analytics/by-date?start_date=2025-01-01&end_date=2025-01-31").status_code != 200:
				print("✗ /analytics/by-date returned non-200")
				return False

			if client.get("/analytics/by-lead/lead_1").status_code != 200:
				print("✗ /analytics/by-lead returned non-200")
				return False

			if client.get("/analytics/top-leads?limit=5").status_code != 200:
				print("✗ /analytics/top-leads returned non-200")
				return False

			if client.get("/analytics/time-of-day").status_code != 200:
				print("✗ /analytics/time-of-day returned non-200")
				return False

			if client.get("/analytics/day-of-week").status_code != 200:
				print("✗ /analytics/day-of-week returned non-200")
				return False

			if client.get("/analytics/engagement?days=7").status_code != 200:
				print("✗ /analytics/engagement returned non-200")
				return False

			export_response = client.get("/analytics/export")
			if export_response.status_code != 200 or "text/csv" not in export_response.headers.get("content-type", ""):
				print("✗ /analytics/export returned invalid response")
				return False

		print("✓ Endpoint responses verified")
		print()
		return True

	except Exception as e:
		print(f"✗ Endpoint response test failed: {e}")
		return False


def main():
	"""Run all Email Open Discord Notifier feature tests."""
	print("\n" + "=" * 60)
	print("EMAIL OPEN DISCORD NOTIFIER TEST SUITE")
	print("=" * 60)
	print()

	results = []
	results.append(("Feature 1: App Structure", test_app_structure()))
	results.append(("Feature 2: API Routes", test_routes_registered()))
	results.append(("Feature 3: README", test_readme_documentation()))
	results.append(("Feature 4: Endpoint Responses", test_endpoints_response()))

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
