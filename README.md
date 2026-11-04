# CHANGE ORDER

A client asks for "one more thing" in a shared channel. Their agent and the freelancer's agent settle it from private files the other side can't see, and it binds only when each person approves their own agent.

Entry for Flip the Switch, Best Business Workflow. Maya, Theo and Northbeam Coffee are fictional.

## What happens

Maya, the client, writes in the channel: "I would like the site in French too before launch. All 12 pages if we can."

| Step | Theo's agent offers | Maya's agent |
|---|---|---|
| 1 | 12 pages, $4,180, launch Dec 7 | No |
| 2 | 6 pages, $2,470, launch Dec 4 | No |
| 3 | 4 pages, $1,900, launch Dec 3 | Yes |

The room only ever sees offers and yes or no. Maya's $2,000 signing limit and Theo's lowest rate stay in their own folders. Prices come from a script, and the yes or no comes from a script, so the agents don't do the maths or see the limit.

Then both agents ask to sign. Each request appears as an approval card in the channel. If Maya presses Approve on Theo's card, she sees "Your answer to A1 did not land, because you may not address this agent, so you may not answer it," and nothing is signed. Each person approves their own card, both records carry the same fingerprint of the terms, and Maya's agent saves a "Signed change order" document in the room.

From Maya's message to both cards took about 80 seconds in our runs.

## The agents

| | Maya's agent | Theo's agent |
|---|---|---|
| Works for | Maya, the client | Theo, the freelancer |
| Runs on | Codex, in `fixtures/client/` | Codex, in `fixtures/freelancer/` |
| Private file | `budget.json` | `rates.json` |
| Its tool | `tools/check_offer.py` answers yes or no | `tools/quote.py` computes price and date |
| May run alone | its check, reading the contract | its quote, reading the contract |
| Needs its owner's card | `tools/sign.py` | `tools/sign.py` |

Instructions are in `agents/`. Command rules are in `codex/`.

## What Switch does here

Switch is what lets two people's agents share a room and still answer to different people.

- **Two owners, one room.** Maya and Theo each own an agent, and each agent runs from that owner's own controller. Both join one Mattermost channel through Switch.
- **Addressing policy.** Each agent accepts messages only from its owner and the other agent (`scripts/create_agents.py`).
- **Approval cards.** A command outside the rules pauses the agent and posts a card. Switch records who chose.
- **Refusal.** Whoever may not address an agent may not answer its cards. This is the rule that stops Maya approving for Theo, and Switch enforces it, not our prompts.
- **Room document.** The final terms are saved in the room through Switch.

Without Switch there is no shared room with separate owners, and no check on who approved. You would be left with two chatbots and a promise.

## Channel setup

Mattermost, bundled with the Switch stack. `scripts/reset_room.sh` does all of this:

1. Maya creates a private channel and adds Theo.
2. Maya adds `maya-agent`.
3. Theo sends `!invite-agent @theo-agent`.

## Run it

You need Docker, [uv](https://docs.astral.sh/uv/), a signed-in Codex CLI (`codex login`), and the Switch controller 0.31.0:

```bash
npm install --global --ignore-scripts https://github.com/sandbox-quantum/switch/releases/download/switch-agent-controller-v0.31.0/switch-agent-controller-0.31.0.tgz
```

Then, from this folder:

```bash
sh scripts/setup.sh
```

This generates fresh secrets, starts the stack, creates Maya and Theo, enrolls a controller for each, creates the agents and opens the channel. We ran it from a clean copy of this folder on a separate stack, and the whole deal below completed.

Open two windows so each person has their own login. Logins are in `runtime/owners.json`.

- Maya: http://127.0.0.1:8065
- Theo: http://localhost:8065

Open the "Northbeam change orders" channel and post this as Maya:

```text
@maya-agent I would like the site in French too before launch. All 12 pages if we can. Please sort it out with @theo-agent.
```

The approval cards appear inside threads, not in the main channel view. Open the thread with "2 replies" under the latest offer, or go to Threads in the sidebar. Theo's is under Maya's agent's last message, and Maya's is under Theo's agent's last message.

To start over:

```bash
sh scripts/reset_room.sh northbeam-demo
```

## What we checked

Screens and logs are in `evidence/`.

- The full flow by clicking in the real Mattermost app, as Maya and Theo in separate logins.
- Maya pressing Approve on Theo's card is refused on her screen. Typing `A1 1` as Maya does nothing either. No file was signed after either attempt.
- Both signed records hold the same terms and fingerprint.
- A search of the room for the private figures and notes found none.
- Maya pressing Stop on Theo's agent, while his card was waiting, did not stop it. No refusal is shown to her, though. The press just has no effect.

## Limits

- **Privacy rests on rules and instructions, not a wall.** In this demo both folders are on one Mac. The rules forbid an agent from reading its private file, and any other command raises a card, but an owner who approved a command reading the other folder would let it through. We have not run the agents on separate machines, which is what would make this a hard boundary.
- **The limit on messages is an instruction.** Agents are told to use at most 4 messages to reach terms. Nothing enforces it.
- **The signature is a recorded approval.** It is not legally binding.
- **The negotiation is simple.** Theo's agent steps down 12, 6, 4 pages at list price. Below 4 it hands back to Theo.
- **Wording varies.** Agents phrase the scope differently between runs, so the fingerprint changes from run to run. Price and date did not change across our runs. Within a run the two fingerprints must match.
- **Off-script questions can go unanswered.** Asked by Theo to summarize the contract, his agent finished without posting a reply.
- **Cards are easy to miss.** They sit in threads, which is how Switch posts them.
- **It costs Codex usage.** We hit a usage limit once during testing, so check your allowance before a live demo.

## Layout

```text
agents/     instructions for each agent
codex/      which commands each agent may run without asking
fixtures/   each side's private folder, contract and tools
scripts/    setup, reset, and `mm` for acting as Maya or Theo from the terminal
stack/      Switch 0.31.0 compose file and settings template
evidence/   transcript, refusal log, screenshots
```
