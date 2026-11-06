"""Once both sides have signed the same terms, record the deal in Theo's own books.

Touches only this folder: books/invoice-draft.md and books/schedule.json.
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

home = Path(__file__).parent.parent
p = argparse.ArgumentParser()
p.add_argument("--fingerprint", required=True)
p.add_argument("--their-fingerprint", required=True)
a = p.parse_args()
if a.fingerprint != a.their_fingerprint:
    raise SystemExit(json.dumps({"recorded": False, "reason": "fingerprints differ"}))
signed = home / "signed" / f"{a.fingerprint[:12]}.json"
if not signed.exists():
    raise SystemExit(json.dumps({"recorded": False, "reason": "Theo has not signed these terms"}))
terms = json.loads(signed.read_text())["terms"]
books = home / "books"
books.mkdir(exist_ok=True)
state = books / "schedule.json"
schedule = json.loads(state.read_text()) if state.exists() else {"launch": "2026-12-01", "change_orders": []}
entry = f"CO-{a.fingerprint[:6]}"
if all(c["entry"] != entry for c in schedule["change_orders"]):
    schedule["change_orders"].append({"entry": entry, "fingerprint": a.fingerprint, **terms,
                                      "recorded_at": datetime.now(timezone.utc).isoformat()})
    schedule["launch"] = max(schedule["launch"], terms["launch"])
    state.write_text(json.dumps(schedule, indent=2))
lines = ["# Invoice draft: Northbeam Coffee (Theo)", "",
         "- Base contract: 12-page marketing site, $18,400"]
for c in schedule["change_orders"]:
    lines.append(f"- {c['entry']}: {c['scope']}, ${c['price_usd']:,} (signed change order {c['fingerprint'][:12]})")
total = 18400 + sum(c["price_usd"] for c in schedule["change_orders"])
lines += ["", f"Total: ${total:,}", f"Launch: {schedule['launch']}", ""]
(books / "invoice-draft.md").write_text("\n".join(lines))
print(json.dumps({"recorded": True, "entry": entry}))
