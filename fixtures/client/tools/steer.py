"""Change Maya's limits for this deal from her private message to her agent.

Writes guidance.json beside budget.json; check_offer.py reads it on the next
check. The limit can never exceed the contingency still uncommitted.
"""
import argparse
import json
from datetime import date
from pathlib import Path

home = Path(__file__).parent.parent
budget = json.loads((home / "budget.json").read_text())
books = home / "books/commitments.json"
committed = sum(c["price_usd"] for c in json.loads(books.read_text())) if books.exists() else 0
guidance_file = home / "guidance.json"
guidance = json.loads(guidance_file.read_text()) if guidance_file.exists() else {}
p = argparse.ArgumentParser()
p.add_argument("--limit-usd", type=int)
p.add_argument("--latest-launch")
a = p.parse_args()
capped = False
if a.limit_usd is not None:
    room = budget["contingency_remaining_usd"] - committed
    capped = a.limit_usd > room
    guidance["maya_signing_limit_usd"] = min(a.limit_usd, room)
if a.latest_launch:
    guidance["latest_acceptable_launch"] = date.fromisoformat(a.latest_launch).isoformat()
guidance_file.write_text(json.dumps(guidance, indent=2))
print(json.dumps({"now_in_effect": guidance, "capped_at_contingency": capped}))
