"""Act in Mattermost as Maya or Theo, the way each would in the app."""
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
MM = "http://127.0.0.1:8065/api/v4"
ENV = dict(
    line.split("=", 1)
    for line in (ROOT / "stack/.env").read_text().splitlines()
    if "=" in line and not line.startswith("#")
)
STATE = json.loads((ROOT / "runtime/owners.json").read_text())
CHANNEL_FILE = ROOT / "runtime/channel.json"


def session(handle):
    r = requests.post(f"{MM}/users/login", json={"login_id": handle, "password": STATE[handle]["password"]})
    r.raise_for_status()
    s = requests.Session()
    s.headers["Authorization"] = "Bearer " + r.headers["Token"]
    return s


def user_id(s, username):
    return s.get(f"{MM}/users/username/{username}").json()["id"]


def channel(name="northbeam-french"):
    if CHANNEL_FILE.exists():
        return json.loads(CHANNEL_FILE.read_text())["id"]
    maya = session("maya")
    team = maya.get(f"{MM}/teams/name/{ENV['MATTERMOST_TEAM_NAME']}").json()["id"]
    r = maya.post(f"{MM}/channels", json={"team_id": team, "name": name, "display_name": "Northbeam change orders", "type": "P"})
    assert r.ok, r.text[:300]
    cid = r.json()["id"]
    CHANNEL_FILE.write_text(json.dumps({"id": cid}))
    return cid


def new(name):
    print("channel", channel(name))


def archive_old():
    """Archive earlier demo rooms so the sidebar shows only the current one."""
    maya = session("maya")
    team = maya.get(f"{MM}/teams/name/{ENV['MATTERMOST_TEAM_NAME']}").json()["id"]
    me = maya.get(f"{MM}/users/me").json()["id"]
    for c in maya.get(f"{MM}/users/{me}/teams/{team}/channels").json():
        if c["display_name"] == "Northbeam change orders":
            print("archive", c["name"], maya.delete(f"{MM}/channels/{c['id']}").status_code)


def add(handle, username):
    s = session(handle)
    r = s.post(f"{MM}/channels/{channel()}/members", json={"user_id": user_id(s, username)})
    print("add", username, "by", handle, r.status_code, "" if r.ok else r.text[:200])


def say(handle, text):
    r = session(handle).post(f"{MM}/posts", json={"channel_id": channel(), "message": text})
    print("say", handle, r.status_code, "" if r.ok else r.text[:200])


def show(limit=30, full=False):
    s = session("maya")
    posts = s.get(f"{MM}/channels/{channel()}/posts", params={"per_page": limit}).json()
    names = {}
    for pid in reversed(posts["order"]):
        p = posts["posts"][pid]
        uid = p["user_id"]
        names.setdefault(uid, s.get(f"{MM}/users/{uid}").json().get("username", uid[:8]))
        when = datetime.fromtimestamp(p["create_at"] / 1000).strftime("%H:%M:%S")
        attachments = p.get("props", {}).get("attachments")
        print(f"[{when}] {names[uid]} {p['type'] or ''} id={pid[:6]}: {p['message']}")
        if attachments:
            print("   attachments:", json.dumps(attachments)[:1500 if full else 500])


def press(handle, post_prefix, label):
    """Press a card's button as this person, as the app does."""
    s = session(handle)
    posts = s.get(f"{MM}/channels/{channel()}/posts", params={"per_page": 100}).json()["posts"]
    post = next(p for pid, p in posts.items() if pid.startswith(post_prefix))
    actions = post["props"]["attachments"][0]["actions"]
    action = next(a for a in actions if label.lower() in a["name"].lower())
    r = s.post(f"{MM}/posts/{post['id']}/actions/{action['id']}", json={})
    print("press", handle, action["name"], r.status_code, r.text[:300])


def drive(seconds="150"):
    """Approve routine cards as their owners and stop at the first signing card."""
    s = session("maya")
    owners = {user_id(s, "maya-agent"): "maya", user_id(s, "theo-agent"): "theo"}
    done = set()
    end = time.time() + int(seconds)
    while time.time() < end:
        posts = s.get(f"{MM}/channels/{channel()}/posts", params={"per_page": 100}).json()["posts"]
        for pid, p in sorted(posts.items(), key=lambda kv: kv[1]["create_at"]):
            if pid in done or "Permission needed" not in p["message"]:
                continue
            actions = (p.get("props", {}).get("attachments") or [{}])[0].get("actions") or []
            if not any("Approve" in a["name"] for a in actions):
                continue
            if "sign.py" in p["message"]:
                print("SIGNING CARD", pid[:6], "for", owners[p["user_id"]], p["message"].splitlines()[-2][:220])
                return
            done.add(pid)
            press(owners[p["user_id"]], pid[:6], "Approve")
        time.sleep(4)
    print("no signing card yet")


if __name__ == "__main__":
    cmd, *args = sys.argv[1:]
    {"new": new, "archive-old": archive_old, "add": add, "say": say, "press": press, "drive": drive, "show": lambda *a: show(*(int(x) for x in a))}[cmd](*args)
