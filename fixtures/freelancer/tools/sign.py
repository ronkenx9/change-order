"""Record this owner's agreement to exact terms and print the terms' fingerprint.

Running this is the signature, so the agent must get its owner's approval first.
The record shows who approved; it is not a legally binding signature.
"""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("--signer", required=True)
p.add_argument("--scope", required=True)
p.add_argument("--price", type=int, required=True)
p.add_argument("--launch", required=True)
a = p.parse_args()
terms = {"scope": a.scope, "price_usd": a.price, "launch": a.launch}
fingerprint = hashlib.sha256(json.dumps(terms, sort_keys=True).encode()).hexdigest()
out = Path(__file__).parent.parent / "signed"
out.mkdir(exist_ok=True)
record = {"signer": a.signer, "terms": terms, "fingerprint": fingerprint,
          "signed_at": datetime.now(timezone.utc).isoformat()}
(out / f"{fingerprint[:12]}.json").write_text(json.dumps(record, indent=2))
print(json.dumps(record))
