"""Once both sides have signed the same terms, record the deal in Maya's own books.

Touches only this folder: books/commitments.json and books/ledger.md.
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
    raise SystemExit(json.dumps({"recorded": False, "reason": "Maya has not signed these terms"}))
terms = json.loads(signed.read_text())["terms"]
books = home / "books"
books.mkdir(exist_ok=True)
state = books / "commitments.json"
commitments = json.loads(state.read_text()) if state.exists() else []
entry = f"CO-{a.fingerprint[:6]}"
if all(c["entry"] != entry for c in commitments):
    commitments.append({"entry": entry, "fingerprint": a.fingerprint, "counterparty": "Theo", **terms,
                        "recorded_at": datetime.now(timezone.utc).isoformat()})
    state.write_text(json.dumps(commitments, indent=2))
budget = json.loads((home / "budget.json").read_text())
left = budget["contingency_remaining_usd"] - sum(c["price_usd"] for c in commitments)
lines = ["# Northbeam website: Maya's books (private)", "",
         f"Contingency at start: ${budget['contingency_remaining_usd']:,}", ""]
for c in commitments:
    lines.append(f"- {c['entry']}: {c['scope']}, ${c['price_usd']:,} to Theo, launch moves to {c['launch']}")
lines += ["", f"Contingency left: ${left:,}", ""]
(books / "ledger.md").write_text("\n".join(lines))
print(json.dumps({"recorded": True, "entry": entry}))
