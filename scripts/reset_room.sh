#!/bin/sh
# Start clean: stop the controllers, drop these two agents' sessions, signed
# records, books and private steering, restart, and open a new channel with
# both agents and the privacy check in it.
cd "$(dirname "$0")/.." || exit 1
pkill -f 'switch-agent-controller run --data-dir runtime/controllers'
pkill -f 'scripts/privacy_check.py'
sleep 2
python3 - <<'PY'
import glob, json, os, shutil
state = json.load(open("runtime/owners.json"))
ours = {state["maya"]["agent_id"], state["theo"]["agent_id"]}
for events in glob.glob(os.path.expanduser("~/.local/state/switch/sdk-sessions/*/events.jsonl")):
    first = json.loads(open(events).readline())["body"]["session"]["agentId"]
    if first in ours:
        shutil.rmtree(os.path.dirname(events))
PY
rm -rf fixtures/client/signed fixtures/freelancer/signed fixtures/client/books fixtures/freelancer/books \
  fixtures/client/guidance.json runtime/channel.json
nohup scripts/run_controllers.sh >/dev/null 2>&1 &
sleep 7
scripts/mm archive-old
scripts/mm clear-dm maya
scripts/mm clear-dm theo
scripts/mm new "$1"
scripts/mm add maya theo
scripts/mm add maya maya-agent
sleep 4
scripts/mm say theo '!invite-agent @theo-agent'
sleep 6
nohup uv run -q --no-project --with requests python -I scripts/privacy_check.py --wait \
  > runtime/logs/privacy-check.log 2>&1 &
