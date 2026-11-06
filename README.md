# CHANGE ORDER

A client asks for "one more thing" in a shared channel. Their agent and the freelancer's agent settle it from private files the other side can't see, and it binds only when each person approves their own agent.

Entry for Flip the Switch, Best Business Workflow. Maya, Theo and Northbeam Coffee are fictional.

## What happens

**1. Maya steers her own agent in private.** In a direct message only she and her agent can see, Maya writes: "I can go up to $2,500 if that gets us more pages in French. Launch still has to be on or before Dec 8." Her agent applies it to her private limits and confirms to her. Theo never sees this message or the reason.

**2. Maya asks in the shared channel:** "I would like the site in French too before launch. All 12 pages if we can."

| Step | Theo's agent offers | Maya's agent |
|---|---|---|
| 1 | 12 pages, $4,180, launch Dec 7 | No |
| 2 | 6 pages, $2,470, launch Dec 4 | Yes |

Without Maya's private note her default limit is $2,000, so step 2 is a no and the deal settles at 4 pages for $1,900. With the note she gets 6 pages. The room only ever sees offers and yes or no. Prices come from a script, and the yes or no comes from a script, so the agents don't do the maths or see the limit.

**3. Each person approves their own agent.** Both agents ask to sign, and each request appears as an approval card. If Maya presses Approve on Theo's card, she sees "Your answer to A1 did not land, because you may not address this agent, so you may not answer it," and nothing is signed. Each person approves their own card, and both records carry the same fingerprint of the terms.

**4. The deal lands in each side's own books.** Once the fingerprints match, each agent records the deal in its own folder only. Maya's ledger shows the $2,470 commitment and her contingency left ($30). Theo's invoice draft gets the new line and a new total ($20,870), and his schedule moves launch to Dec 4. Maya's agent saves a "Signed change order" document in the room.

**5. A privacy check posts in the room.** It reads every message in the channel and checks it against each side's own private terms: limits, rates, booked dates, the reason behind the date. It posts only the counts ("Maya's private terms: 7 checked, 0 found"), never the terms.

From Maya's message to both signing cards took about 2.5 minutes in our last run.

## The agents

| | Maya's agent | Theo's agent |
|---|---|---|
| Works for | Maya, the client | Theo, the freelancer |
| Runs on | Codex, in `fixtures/client/` | Codex, in `fixtures/freelancer/` |
| Private files | `budget.json`, `guidance.json` (Maya's steering), `books/` | `rates.json`, `books/` |
| Its tools | `tools/check_offer.py` answers yes or no; `tools/steer.py` applies Maya's private note | `tools/quote.py` computes price and date |
| May run alone | its check, steering, recording a matched deal, reading the contract | its quote, recording a matched deal, reading the contract |
| Needs its owner's card | `tools/sign.py` | `tools/sign.py` |

Instructions are in `agents/`. Command rules are in `codex/`.

## What Switch does here

Switch is what lets two people's agents share a room and still answer to different people.

- **Two owners, one room.** Maya and Theo each own an agent, and each agent runs from that owner's own controller. Both join one Mattermost channel through Switch.
- **Addressing policy.** Each agent accepts messages only from its owner and the other agent (`scripts/create_agents.py`).
- **Approval cards.** A command outside the rules pauses the agent and posts a card. Switch records who chose.
- **Refusal.** Whoever may not address an agent may not answer its cards. This is the rule that stops Maya approving for Theo, and Switch enforces it, not our prompts.
- **Private line to your own agent.** Maya's direct message to her agent goes through Switch to the same agent, under the same policy, and never enters the shared room.
- **Room document.** The final terms are saved in the room through Switch.

Without Switch there is no shared room with separate owners, and no check on who approved. You would be left with two chatbots and a promise.

## Channel setup

Mattermost, bundled with the Switch stack. `scripts/reset_room.sh` does all of this:

1. Maya creates a private channel and adds Theo.
2. Maya adds `maya-agent`.
3. Theo sends `!invite-agent @theo-agent`.
4. The privacy check joins and waits for the signed change order.

The reset also clears each owner's direct messages with their agent, each side's books and Maya's steering.

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

As Maya, open a direct message with Maya's agent and send:

```text
Private note for this change: I can go up to $2,500 if that gets us more pages in French. Launch still has to be on or before Dec 8.
```

Then open the "Northbeam change orders" channel and post this as Maya:

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

- The full flow by clicking in the real Mattermost app, as Maya and Theo in separate logins, including Maya's private note in her direct message, both approvals, the books and the privacy card (`evidence/ui/`). Theo's sidebar has no view of Maya's direct message.
- Maya pressing Approve on Theo's card is refused on her screen. Typing `A1 1` as Maya does nothing either. No file was signed after either attempt.
- Both signed records hold the same terms and fingerprint.
- A search of the room for the private figures and notes found none. The privacy check card now does this in the room after every deal, and flags a hit by name in red (tested offline against planted leaks such as "$2,000", "2k", "Dec 9", "$95/h" and "booked until November 27").
- Maya's private note changed the result: 6 pages at $2,470 instead of 4 at $1,900. The note is only in her direct messages (`evidence/maya-private-steering.txt`), and the room transcript has no trace of it.
- After both signed, Maya's ledger and Theo's invoice were each updated in their own folder only (`evidence/maya-books-after.md`, `evidence/theo-invoice-after.md`).
- In one run the agents posted their fingerprints without mentioning each other, so neither woke up to record the deal. The instructions now require the mention. A full run after that fix finished on its own, with books, the room document and the privacy card, and no message from either person after the request (`evidence/room-transcript-no-nudge.txt`).
- Maya pressing Stop on Theo's agent, while his card was waiting, did not stop it. No refusal is shown to her, though. The press just has no effect.

## Limits

- **Privacy rests on rules and instructions, not a wall.** In this demo both folders are on one Mac. The rules forbid an agent from reading its private file, and any other command raises a card, but an owner who approved a command reading the other folder would let it through. We have not run the agents on separate machines, which is what would make this a hard boundary.
- **The limit on messages is an instruction.** Agents are told to use at most 4 messages to reach terms. Nothing enforces it.
- **The signature is a recorded approval.** It is not legally binding.
- **The privacy check matches patterns.** It catches the figures, dates and phrases it knows in common spellings. A paraphrase such as "she can't spend much more than two grand" would get past it.
- **Steering works through a file.** Maya's direct message is a separate agent session, so it changes her limits by writing her private guidance file, which the offer check reads. The room session isn't told the note exists.
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
scripts/    setup, reset, privacy check, and `mm` for acting as Maya or Theo from the terminal
stack/      Switch 0.31.0 compose file and settings template
evidence/   transcript, private steering, books after the deal, refusal log, screenshots
```
