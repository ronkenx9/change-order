#!/bin/sh
# One command from a fresh clone to a ready room. Needs Docker, uv, the Switch
# agent controller 0.31.0, and a signed-in Codex CLI.
cd "$(dirname "$0")/.." || exit 1
PROJECT=${COMPOSE_PROJECT:-changeorder}
for tool in docker uv switch-agent-controller; do
  command -v "$tool" >/dev/null || { echo "missing: $tool" >&2; exit 1; }
done
[ -f "$HOME/.codex/auth.json" ] || { echo "sign in to Codex first: codex login" >&2; exit 1; }
py() { uv run -q --no-project --with requests python -I "$@"; }
[ -f stack/.env ] || py scripts/init_env.py
(cd stack && docker compose --profile collab --profile gateway -p "$PROJECT" up -d) || exit 1
echo "waiting for Switch's first-run setup (creates the admins and the Mattermost link)"
for _ in $(seq 1 120); do
  state=$(cd stack && docker compose --profile collab --profile gateway -p "$PROJECT" ps -a setup --format '{{.State}}')
  [ "$state" = exited ] && break
  sleep 3
done
[ "$state" = exited ] || { echo "setup did not finish; see: docker compose -p $PROJECT logs setup" >&2; exit 1; }
mkdir -p runtime
py scripts/setup_owners.py || exit 1
py scripts/enroll_controllers.py || exit 1
nohup scripts/run_controllers.sh >/dev/null 2>&1 &
sleep 7
py scripts/create_agents.py || exit 1
sh scripts/reset_room.sh "northbeam-$(date +%H%M)"
echo "ready: http://localhost:8065 (logins are in runtime/owners.json)"
