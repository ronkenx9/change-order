#!/bin/sh
# Run one controller per owner, each with a clean Codex home: the login plus
# that owner's command rules, and none of this machine's personal instructions,
# skills or plugins. tools/sign.py is in no rules file, so it always asks.
cd "$(dirname "$0")/.." || exit 1
ROOT=$(pwd)
mkdir -p runtime/logs
for handle in maya theo; do
  home="$ROOT/runtime/codex-home/$handle"
  mkdir -p "$home/rules"
  ln -sf "$HOME/.codex/auth.json" "$home/auth.json"
  cp "codex/$handle.rules" "$home/rules/change-order.rules"
  printf 'model_reasoning_effort = "medium"\n' > "$home/config.toml"
  CODEX_HOME="$home" switch-agent-controller run --data-dir "runtime/controllers/$handle" \
    > "runtime/logs/$handle-controller.log" 2>&1 &
done
wait
