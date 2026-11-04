"""Write stack/.env from the template, with a fresh random value for every secret."""
import re
import secrets
from pathlib import Path

STACK = Path(__file__).resolve().parent.parent / "stack"
target = STACK / ".env"
if target.exists():
    raise SystemExit("stack/.env already exists; delete it first to regenerate every secret.")
lines = []
for line in (STACK / ".env.example").read_text().splitlines(keepends=True):
    m = re.match(r"^([A-Z0-9_]+)=$", line.strip())
    if m and m.group(1) == "SECRET_KEYS":
        line = f"SECRET_KEYS=local:{secrets.token_hex(32)}\n"
    elif m and re.search("PASSWORD|SECRET|TOKEN|KEY", m.group(1)):
        line = f"{m.group(1)}={secrets.token_hex(24)}\n"
    lines.append(line)
target.write_text("".join(lines))
target.chmod(0o600)
print("wrote stack/.env")
