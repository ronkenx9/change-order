"""Check an offer against Maya's private limits. Prints only a verdict for the agent.

Maya's private steering (guidance.json, written by steer.py) overrides the defaults.
"""
import argparse
import json
from datetime import date
from pathlib import Path

home = Path(__file__).parent.parent
budget = json.loads((home / "budget.json").read_text())
if (home / "guidance.json").exists():
    budget.update(json.loads((home / "guidance.json").read_text()))
p = argparse.ArgumentParser()
p.add_argument("--price", type=int, required=True)
p.add_argument("--launch", required=True)
a = p.parse_args()
price_ok = a.price <= budget["maya_signing_limit_usd"]
date_ok = date.fromisoformat(a.launch) <= date.fromisoformat(budget["latest_acceptable_launch"])
print(json.dumps({"price_within_limit": price_ok, "launch_acceptable": date_ok, "can_recommend": price_ok and date_ok}))
