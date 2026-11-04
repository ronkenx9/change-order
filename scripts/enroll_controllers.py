"""Enroll one agent controller per owner, each with its own data directory."""
import json
import subprocess
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
API = "http://127.0.0.1:8000/gateway"
STATE = ROOT / "runtime/owners.json"
EMAILS = {"maya": "maya@example.test", "theo": "theo@example.test"}


def main():
    state = json.loads(STATE.read_text())
    for handle, email in EMAILS.items():
        data_dir = ROOT / "runtime/controllers" / handle
        if (data_dir / "identity.json").exists() or state[handle].get("controller_id"):
            print(handle, "already enrolled")
            continue
        data_dir.mkdir(parents=True, exist_ok=True)
        s = requests.Session()
        s.post(f"{API}/auth/login", json={"email": email, "password": state[handle]["password"]}).raise_for_status()
        r = s.post(f"{API}/management/enrollment-codes")
        assert r.ok, (r.status_code, r.text[:300])
        code = r.json()["code"]
        out = subprocess.run(
            ["switch-agent-controller", "enroll", "--server", "http://127.0.0.1:8000", "--code", code,
             "--name", f"{handle}-machine", "--description", f"{handle}'s machine", "--data-dir", str(data_dir),
             "--secret-store", "file"],
            capture_output=True, text=True,
        )
        print(handle, out.returncode, out.stdout.strip()[:300], out.stderr.strip()[:300])
        out.check_returncode()
        controllers = s.get(f"{API}/management/controllers").json()
        print(json.dumps(controllers)[:400])
        items = controllers if isinstance(controllers, list) else controllers.get("controllers", controllers.get("items"))
        state[handle]["controller_id"] = items[0]["id"]
    STATE.write_text(json.dumps(state, indent=2))
    STATE.chmod(0o600)


if __name__ == "__main__":
    main()
