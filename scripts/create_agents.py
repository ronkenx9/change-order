"""Create each owner's agent, then let it answer only its owner and the other agent.

Whoever may address an agent may answer its approval cards, so this policy is
what keeps each owner's approvals their own.
"""
import json
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
API = "http://127.0.0.1:8000/gateway"
STATE = ROOT / "runtime/owners.json"
AGENTS = {
    "maya": {"name": "maya-agent", "display": "Maya's agent", "email": "maya@example.test", "dir": "client",
             "description": "Represents the client in change orders."},
    "theo": {"name": "theo-agent", "display": "Theo's agent", "email": "theo@example.test", "dir": "freelancer",
             "description": "Represents the freelancer in change orders."},
}


def main():
    state = json.loads(STATE.read_text())
    shared = (ROOT / "agents/shared.md").read_text()
    sessions = {}
    for handle, spec in AGENTS.items():
        s = requests.Session()
        s.post(f"{API}/auth/login", json={"email": spec["email"], "password": state[handle]["password"]}).raise_for_status()
        sessions[handle] = s
        existing = [a for a in s.get(f"{API}/management/agents").json() if a["name"] == spec["name"]]
        definition = {
            "provider": "codex", "auto_mode": False, "auto_approve": False,
            "instructions": (ROOT / f"agents/{handle}.md").read_text() + "\n" + shared,
            "directory": str(ROOT / "fixtures" / spec["dir"]),
        }
        if existing:
            state[handle]["agent_id"] = existing[0]["agent_id"]
            r = s.patch(f"{API}/management/agents/{existing[0]['agent_id']}", json={"definition": definition})
            assert r.ok, (r.status_code, r.text[:600])
            continue
        body = {
            "name": spec["name"], "description": spec["description"], "display_name": spec["display"],
            "controller_id": state[handle]["controller_id"], "desired_state": "running",
            "definition": definition,
        }
        r = s.post(f"{API}/management/agents", json=body)
        assert r.ok, (r.status_code, r.text[:600])
        state[handle]["agent_id"] = r.json()["agent_id"]
    STATE.write_text(json.dumps(state, indent=2))
    STATE.chmod(0o600)

    for me, other in (("maya", "theo"), ("theo", "maya")):
        policy = {"rules": [{"users": [], "agents": [state[other]["agent_id"]], "owner": True}]}
        r = sessions[me].put(f"{API}/agents/{state[me]['agent_id']}/addressing-policy", json={"policy": policy})
        assert r.ok, (r.status_code, r.text[:600])
        stored = r.json()["addressing_policy"]
        assert stored["rules"], "an empty rule list would open the agent to anyone"
        print(me, "policy", json.dumps(stored)[:300])


if __name__ == "__main__":
    main()
