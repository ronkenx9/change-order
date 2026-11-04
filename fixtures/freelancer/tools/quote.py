"""Price added translated pages from Theo's private rates. All arithmetic lives here."""
import argparse
import json
import math
from datetime import date, timedelta
from pathlib import Path

rates = json.loads((Path(__file__).parent.parent / "rates.json").read_text())
p = argparse.ArgumentParser()
p.add_argument("--pages", type=int, required=True)
a = p.parse_args()
hours = rates["translation_setup_hours"] + a.pages * rates["hours_per_translated_page"]
over = max(0, hours - rates["free_hours_before_launch"])
slip_days = math.ceil(over / rates["hours_per_day"])
launch = date(2026, 12, 1) + timedelta(days=slip_days)
print(json.dumps({
    "pages": a.pages,
    "hours": hours,
    "list_price_usd": hours * rates["list_rate_usd_per_hour"],
    "lowest_price_usd": hours * rates["floor_rate_usd_per_hour"],
    "earliest_launch": launch.isoformat(),
}))
