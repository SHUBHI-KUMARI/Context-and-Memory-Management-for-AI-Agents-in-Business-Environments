"""Seed sample memory data into the running backend server.

Beginner-friendly notes:
- Your current vector store is IN-MEMORY.
- That means data lives inside the running FastAPI process.
- So to seed data for a demo, we send HTTP requests to the API.

How to use:
1) Start the server (from backend/):
   uvicorn app.main:app --reload

2) In a new terminal (still from backend/):
   python3 seed_data.py

Optional:
- Change the server URL:
   python3 seed_data.py --base-url http://127.0.0.1:8000

Tip:
- If you restart the server, you will lose in-memory data.
  Run this script again to re-seed.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def _months_ago(months: int) -> str:
    """Return an ISO timestamp for roughly `months` months ago.

    We approximate 1 month as 30 days to keep things simple.
    """

    dt = datetime.now(timezone.utc) - timedelta(days=30 * months)
    return dt.isoformat()


def _post_json(url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Send a POST request with JSON and return JSON response."""

    data = json.dumps(payload).encode("utf-8")

    req = Request(
        url=url,
        data=data,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )

    with urlopen(req, timeout=10) as resp:
        body = resp.read().decode("utf-8")
        return json.loads(body)


def build_sample_memories() -> List[Dict[str, Any]]:
    """Create a small list of sample memories for demo/testing."""

    return [
        {
            "type": "historical",
            "content": "Supplier XYZ had quality issues with delivered components 4 months ago.",
            "timestamp": _months_ago(4),
            "metadata": {
                "supplier": "XYZ",
                "issue_type": "quality",
                "severity": "high",
            },
        },
        {
            "type": "historical",
            "content": "Supplier XYZ had a payment dispute about invoice INV-1008 around 8 months ago.",
            "timestamp": _months_ago(8),
            "metadata": {
                "supplier": "XYZ",
                "issue_type": "payment_dispute",
                "invoice": "INV-1008",
            },
        },
        {
            "type": "experiential",
            "content": "Supplier XYZ performed well in the last 2 months with on-time deliveries.",
            "timestamp": _months_ago(2),
            "metadata": {
                "supplier": "XYZ",
                "issue_type": "positive_performance",
                "metric": "on_time_delivery",
            },
        },
        {
            "type": "temporal",
            "content": "Delivery delays increased during monsoon season due to road flooding.",
            "timestamp": _months_ago(1),
            "metadata": {
                "issue_type": "late_delivery",
                "season": "monsoon",
                "cause": "road_flooding",
            },
        },
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed sample memories into the running API")
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:8000",
        help="Base URL for the FastAPI server (default: http://127.0.0.1:8000)",
    )
    args = parser.parse_args()

    base_url: str = args.base_url.rstrip("/")
    add_url = f"{base_url}/memory/add"

    samples = build_sample_memories()

    print(f"Seeding {len(samples)} memories into: {add_url}")

    try:
        for i, payload in enumerate(samples, start=1):
            saved = _post_json(add_url, payload)
            print(f"[{i}/{len(samples)}] Added memory id={saved.get('id')} type={saved.get('type')}")

    except HTTPError as e:
        # The server responded, but with an error code.
        msg = e.read().decode("utf-8", errors="ignore")
        print("\nServer returned an HTTP error.")
        print(f"Status: {e.code}")
        print(f"Body: {msg}")
        return 1

    except URLError as e:
        # Could not connect to the server.
        print("\nCould not connect to the server.")
        print("Make sure the API is running, then try again.")
        print(f"Error: {e}")
        return 1

    print("\nDone. You can now try:")
    print(f"- Search: {base_url}/memory/search?query=Supplier%20XYZ&top_k=5")
    print(f"- Decision: POST {base_url}/decision with body {{'query':'Supplier XYZ','top_k':5}}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
