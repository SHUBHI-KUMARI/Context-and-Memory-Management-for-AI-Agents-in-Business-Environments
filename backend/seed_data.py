import json
from datetime import datetime, timezone, timedelta
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

def get_timestamp_months_ago(months: int) -> str:
    dt = datetime.now(timezone.utc) - timedelta(days=30 * months)
    return dt.isoformat()

def post_memory(url: str, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = Request(
        url=url,
        data=data,
        method="POST",
        headers={"Content-Type": "application/json", "Accept": "application/json"}
    )
    with urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))

DUMMY_DATA = [
    {
        "type": "historical",
        "content": "Supplier XYZ had critical quality issues with delivered microchips 4 months ago.",
        "timestamp": get_timestamp_months_ago(4),
        "metadata": {"supplier": "XYZ", "issue_type": "quality"}
    },
    {
        "type": "historical",
        "content": "Supplier ABC provided a 10% discount on bulk orders, resulting in $5000 savings.",
        "timestamp": get_timestamp_months_ago(8),
        "metadata": {"supplier": "ABC", "issue_type": "discount", "savings": 5000}
    },
    {
        "type": "experiential",
        "content": "Supplier XYZ performed well in the last 2 months with on-time deliveries, resolving prior issues.",
        "timestamp": get_timestamp_months_ago(2),
        "metadata": {"supplier": "XYZ", "issue_type": "positive_performance"}
    },
    {
        "type": "temporal",
        "content": "Shipping delays universally increase during the summer monsoon season due to flooded routes.",
        "timestamp": get_timestamp_months_ago(1),
        "metadata": {"season": "monsoon", "cause": "road_flooding"}
    },
    {
        "type": "experiential",
        "content": "Invoice INV-2034 from Supplier LMN was flagged as duplicate risk.",
        "timestamp": get_timestamp_months_ago(0),
        "metadata": {"supplier": "LMN", "invoice": "INV-2034", "risk": "duplicate"}
    },
]

def main():
    add_url = "http://127.0.0.1:8000/memory/add"
    print(f"Starting seed process to: {add_url}")
    
    success_count = 0
    for payload in DUMMY_DATA:
        try:
            saved = post_memory(add_url, payload)
            success_count += 1
            print(f"✅ Added {payload['type']} memory about: {payload['content'][:30]}...")
        except HTTPError as e:
            msg = e.read().decode("utf-8", errors="ignore")
            print(f"❌ Server Error {e.code}: {msg}")
        except URLError as e:
            print("❌ Connection Error. Is the FastAPI server running?")
            print(f"   Detail: {e}")
            break
            
    print(f"\nDone! Successfully seeded {success_count} dummy memories.")

if __name__ == "__main__":
    main()
