"""Create two owners on the local Switch server and link their Mattermost accounts.

Maya is the client and Theo the freelancer. Both are fictional. Passwords are
generated here and kept in runtime/owners.json, which git ignores.
"""
import json
import secrets
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
ENV = dict(
    line.split("=", 1)
    for line in (ROOT / "stack/.env").read_text().splitlines()
    if "=" in line and not line.startswith("#")
)
API = "http://127.0.0.1:8000/gateway"
MM = "http://127.0.0.1:8065/api/v4"
STATE = ROOT / "runtime/owners.json"
OWNERS = {
    "maya": {"name": "Maya (client)", "email": "maya@example.test"},
    "theo": {"name": "Theo (freelancer)", "email": "theo@example.test"},
}


def gateway(email, password):
    s = requests.Session()
    r = s.post(f"{API}/auth/login", json={"email": email, "password": password})
    r.raise_for_status()
    return s


def main():
    STATE.parent.mkdir(exist_ok=True)
    state = json.loads(STATE.read_text()) if STATE.exists() else {}
    admin = gateway(ENV["GATEWAY_ADMIN_EMAIL"], ENV["GATEWAY_ADMIN_PASSWORD"])
    r = requests.post(
        f"{MM}/users/login",
        json={"login_id": ENV["MATTERMOST_ADMIN_USER"], "password": ENV["MATTERMOST_ADMIN_PASSWORD"]},
    )
    r.raise_for_status()
    mm_admin = {"Authorization": "Bearer " + r.headers["Token"]}
    team = requests.get(f"{MM}/teams/name/{ENV['MATTERMOST_TEAM_NAME']}", headers=mm_admin).json()["id"]
    bridges = admin.get(f"{API}/collaborations").json()
    print(json.dumps(bridges)[:300])
    first = bridges[0] if isinstance(bridges, list) else (bridges.get("bridges") or bridges.get("items") or bridges.get("collaborations"))[0]
    bridge = first.get("id") or first.get("bridge_id")
    state["bridge_id"] = bridge

    for handle, owner in OWNERS.items():
        entry = state.setdefault(handle, {})
        entry.setdefault("password", "Co-" + secrets.token_urlsafe(18))
        r = admin.post(
            f"{API}/users",
            json={"name": owner["name"], "email": owner["email"], "password": entry["password"]},
        )
        assert r.status_code in (200, 201, 409), (r.status_code, r.text[:200])
        r = requests.post(
            f"{MM}/users",
            json={"email": owner["email"], "username": handle, "password": entry["password"], "first_name": owner["name"]},
            headers=mm_admin,
        )
        assert r.status_code in (200, 201, 400), (r.status_code, r.text[:200])
        mm_id = requests.get(f"{MM}/users/username/{handle}", headers=mm_admin).json()["id"]
        entry["mm_user_id"] = mm_id
        requests.post(f"{MM}/teams/{team}/members", json={"team_id": team, "user_id": mm_id}, headers=mm_admin)

        me = gateway(owner["email"], entry["password"])
        entry["user_id"] = me.get(f"{API}/auth/me").json()["id"]
        r = me.post(
            f"{API}/collaborations/{bridge}/identities",
            json={"external_user_id": mm_id, "username": handle, "expects_confirmation": True},
        )
        assert r.is_redirect is False and r.ok, (r.status_code, r.text[:300])
        identity = r.json()
        if identity.get("link_request") is not None:
            login = requests.post(f"{MM}/users/login", json={"login_id": handle, "password": entry["password"]})
            login.raise_for_status()
            token = login.headers["Token"]
            r = me.post(
                f"{API}/collaborations/{bridge}/identities/{identity['id']}/verify-session",
                json={"token": token},
            )
            requests.post(f"{MM}/users/logout", headers={"Authorization": f"Bearer {token}"})
            assert r.ok, (r.status_code, r.text[:300])
        print(handle, "linked", "user", entry["user_id"][:8], "mm", mm_id[:8])
    STATE.write_text(json.dumps(state, indent=2))
    STATE.chmod(0o600)


if __name__ == "__main__":
    main()
