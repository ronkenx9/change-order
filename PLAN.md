# CHANGE ORDER: plan

Flip the Switch, Best Business Workflow. Submission closes 2026-11-07 19:29 WAT.
Hacking opens 2026-11-03 19:31 WAT. The Switch setup and workflow are built after that, not before.

## Pitch
A client asks for "one more thing" in a shared channel. Their agent and the freelancer's agent settle it from private files the other side can't see, and it binds only when each person approves their own agent.

## Facts from Switch source (commit 8f2c885, read only, nothing run yet)
- Second owner: an admin can create another user with `POST /users` (`gateway/auth_routes.py`).
- Whoever may address an agent may also answer its approval cards (`session_activity/service.py`, `_require_may_address`). So the "anyone" setting would let the client approve the freelancer's agent. Do not use it.
- Required policy: custom, owner plus the one named counterpart agent, no other humans. `owner_only_policy(allowed_agent_ids)` in `addressing.py` is this shape. Set through `update_addressing_policy` in `gateway/agents.py`.
- Refusal text exists: "You may not address this agent, so you may not ...". This is a demo beat.
- Local server needs no Docker but binds to this computer only. Mattermost needs Docker.
- The documented loop prevention is about relaying platform messages, not agents replying to each other. Cap turns ourselves.

## Probes (first, after the window opens; stop and rethink if P1 or P2 fails)
- P1: two owners each running an agent on one server. Agents register with the signed-in Console session, so try a second Console profile, then `POST /agents/register-known` with a token for the second user.
- P2: a gated sign command produces an approval card in the room; the other owner is refused; the approver is recorded. Disable or discourage "Allow for this session" for signing.
- P3: agent-to-agent exchange runs with a turn cap and stops.

## Build
- `fixtures/client/`: budget, brief. `fixtures/freelancer/`: contract, rate card, calendar. Clearly fictional.
- `quote` script: price and date come from deterministic code over the rate card and calendar. Agents write prose about the numbers and never invent them.
- `sign` script: records one party's signature over a hash of the change order, gated by the approval card.
- Agent instructions and a Switch template, so the setup can be reproduced.
- Signed change order saved as a room document.

## Demo (60s)
1. Client asks for dark mode plus Friday delivery.
2. Each agent checks its own folder; neither file enters the room.
3. Agents trade a priced counter.
4. Client taps Allow on the freelancer's card and is refused. Each owner then approves their own.
5. Signed change order lands as a room document with both approvers.

## Do not claim
- That an agent can never leak. Privacy rests on separate folders and instructions.
- That the signature is legally binding. It is a recorded approval.

## Cut order
OMEN second machine, then Slack mirror, then PDF. Never cut: two owners, private folders, per-owner approval.

## Probe results (2026-11-04, Switch 0.31.0, agents on Codex)

Passed in the final run (`evidence/room-transcript.txt`, `evidence/refusal.log`):
- P1: two owners' controllers run on one Mac, and both agents work in one Mattermost room.
- P2: signing raises a card. Maya pressing Approve on Theo's card is refused (`NOT_AUTHORIZED`) and nothing is signed. Each card records who chose: "Chosen by @theo from Mattermost."
- P3: agents stopped by themselves at 12 pages, 6, then 4 at $1,900, launch Dec 3, with matching fingerprints and a room document. The message cap is an instruction only; nothing enforces it.

Learned the hard way:
- An addressing policy with `{"rules": []}` means open to anyone. `create_agents.py` now asserts the rules are not empty.
- Agents inherit `~/.codex` (AGENTS.md, skills, plugins, rules). One tried to read the owner's brain. `run_controllers.sh` gives each owner a clean `CODEX_HOME`.
- Letting an agent read its private file leaked the limit: it countered at exactly $2,000. Rules now forbid `cat` on those files, and Maya's agent only gets yes or no from `check_offer.py`.
- Codex approval-required mode asks for every command unless a rule allows it, so sign.py is gated by being on no allow list.

Checked in the real Mattermost app (2026-11-04, `evidence/ui/`):
- Maya and Theo each clicked through in their own login. Refusal shows on Maya's screen. Typed `A1 1` does nothing. Maya's Stop on Theo's agent had no effect, with no message.
- `scripts/setup.sh` from a clean copy on a separate stack completed a full deal. It caught one bug: owners were created before the Mattermost admin existed.
- Maya's window on 127.0.0.1 needed `MM_SERVICESETTINGS_ALLOWCORSFROM`, or live updates fail.

Still not checked:
- Whether a command outside the rules that targets the other side's folder would be stopped by anything but the card.
- A run with the agents on separate machines.

## Upgrades (2026-11-06, verified in one run through the Mattermost API)
- Private steering: Maya DMs her agent; it runs `steer.py`, which writes `guidance.json`; `check_offer.py` reads it. Result moved from 4 pages $1,900 to 6 pages $2,470. Bug found on the way: steer wrote the wrong key and the check ignored it.
- Books: after matching fingerprints each agent runs `record.py` in its own folder. Maya's ledger and Theo's invoice and schedule update.
- Privacy check: `scripts/privacy_check.py --wait` posts counts per side after the room document lands. 7 + 7 terms, 0 found.
- Clicked through in the real app (01:08–01:12 WAT): DM steering, both own-card approvals, books, privacy card. Screens in evidence/ui/.
