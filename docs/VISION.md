# Vision

Written for future me, for whatever SLM or coding agent I point at this repo, and for anyone who ends up reading it.

This is the honest account rather than a pitch: what I want the app to become, what I actually use today, and which parts I already know are beyond what I can build soon. Read it before touching architecture.

Written 26 Jul 2026, at the start of the second pivot.

## Purpose

The app used to answer one question: *"did I actually do what I planned?"*

It now answers a broader one: *"does this reduce the friction in my day?"*

The original question still matters, but it belongs to a single module rather than to the whole app. This has stopped being a goal tracker that happens to be personal and become a personal system that contains a goal tracker.

## Current state, honestly

I have barely used the app. I still prefer paper.

That is worth recording because it is the most useful piece of evidence I have. Paper wins on capture speed, and nothing I build is going to beat a notebook for getting a thought out of my head. What the app did give me was a way to review what I had been doing across a week, which paper handles badly.

The conclusion I draw: build for retrieval, recall, analysis, and persistence across devices and years. A feature whose value proposition amounts to "the same as writing it down, but on a screen" will not survive contact with my actual habits.

## Modules

In rough order of how much I need them.

### Vault and journal

This is the reason for the pivot.

The failure I am designing against is specific: the laptop dies, the SSD corrupts, and I lose my passwords, my notes, and the accumulated context of whatever I was working on. Rebuilding that costs weeks. The vault exists to make it impossible.

It holds passwords, so they exist on more than one device, and it holds the journal, so I can read it from my phone without opening a laptop.

Decisions already made:

- Journal and secrets unlock independently. Reading a journal entry must not expose the password vault.
- Master password on every launch. No persistent session.
- 2FA required to change a password. Reading is a lower bar than writing.
- Browser autofill, eventually.
- Offline. Not cloud-optional; no cloud.

Crypto design is in ADR-020. `local/rust-toys/05-vault-and-crypto.md` builds up to it.

### Intelligence engine

LogSeq and Obsidian, but better suited to me. The least defined module here and the one I want most.

The problem it solves is that I have more material to get through than I can hold in my head: textbooks, practice sets, exam preparation. That load currently lives in my memory, and holding it there is the actual headache.

What it has to do is take information out of my head and hand it back at the right moment. Triggers and reminders attached to material rather than to dates. Retained context for a specific resource: which textbook, how far into it I am, what I was doing with it.

It also has to make dead time useful. This generalises the DMN rescue list from ADR-015: given ten idle minutes, the engine should tell me what to open and where I left off, so that time goes into upskilling rather than drifting.

### Planner

The existing goal, task and subtask hierarchy, the priority list, and the analytics. All of it survives the migration, but none of it is the headline any more. It becomes the execution layer that the engine feeds.

### Sync

Every module above is worth much less if it is confined to one machine. Sync is what turns the vault into a genuine backup and makes the journal readable from my phone.

The constraint is that it stays completely offline: LAN, device to device, or sneakernet, but never a server I do not own.

I may not succeed at this. I intend to attempt it regardless. Edge compute, cybersecurity and IoT intersect precisely here, and those are the three areas I am most interested in, so the attempt pays for itself even if the feature does not ship.

## On "replacing LLMs from my life"

I have said that, and I have also said the app will have local AI. Those are not in conflict.

What I want to end is my dependence on someone else's LLM service: the round trip, the account, my data leaving the machine, and the fact that it stops working when I am offline or when a company changes its terms. I am not opposed to AI.

Local AI is in scope, for coding assistance on assignments, for exam preparation, and for reading my own journal and activity data to produce a plan. The distinction that matters is that the model runs on my hardware, over my data, with the network disconnected.

The README still states "No AI". That is now inaccurate and needs correcting. Recorded as ADR-023.

## Non-negotiables

A feature that violates one of these does not get built.

1. Offline. No cloud, no servers, no accounts. It has to work when the network does not.
2. Portable data. I can pick the file up and move it. Data I cannot move is not backed up.
3. Personal-first. Features reflect my needs, not those of a hypothetical user. There is no user base. (ADR-001, still in force.)
4. Learning counts. A substantial part of the point is learning Rust properly, so hand-rolled beats imported unless there is a safety reason. (ADR-024.)
5. Small steps, big goals. One module at a time. The long-term vision does not get to block the next useful feature.

## Deferred

Ideas I have raised, considered, and consciously set aside. Recorded so that neither I nor anyone else mistakes them for oversights.

Local AI that reads the entire device and proposes a reorganisation and automation plan. My assessment at the time was that it is too much for now and that I need features that actually help me first. I still think that is correct.

Offline password reset. I sketched a scheme where a reset sends a random number to the app on my phone, then realised the phone needs the vault in order to receive it, so the loop does not close. Genuinely unsolved; see ADR-020.

Splitting into separate apps and repositories per device. My own comment was "how hard can copy pasting and rewiring the code be right?......right?" The answer is that it is hard when the code is tangled and trivial when the core is a crate with no UI in it, which is why ADR-018 exists.

Renaming the app. Stride stays unless something better appears, and that conversation happens after the modules exist rather than before.

## Device scopes

One app for now, with scope varying by device. Desktop gets everything and is the migration target. Mobile gets journal reading, vault access and quick capture, and comes later.

Splitting into separate projects remains on the table.

## Open questions

None of these are blocking yet.

1. Vault recovery. What happens when I forget the master password? Printed recovery codes kept physically, Shamir shares across devices, or accepting that the data is gone.
2. Sync conflicts. Last-write-wins or CRDTs. Journal entries are append-mostly and straightforward; vault entries are mutable and are not.
3. What "better than Obsidian" actually means. At present it is a feeling rather than a specification, and it needs to become a list of behaviours before the engine can be built.
4. Which local model, and how it runs. Deferred until there is data worth feeding it.
5. The name. Deferred by decision. Candidates if I do change it: Ledger, Cairn, Anchor, Keep.
6. What the second factor is, given no server and no cloud. A TOTP seed stored inside the vault is circular, so it is likely a hardware token or a second enrolled device.

## The rest of the docs

- [ADR.md](./ADR.md) — every decision and its rationale, Flask through to Tauri. Start at ADR-017 for the current pivot.
- [LEARNING.md](./LEARNING.md) — the Rust plan and what has actually sunk in.
- [ROADMAP.md](./ROADMAP.md) — what comes next, in order.
- [CONTRIBUTING.md](./CONTRIBUTING.md) — describes the current Flet app until the migration lands.
- `local/rust-toys/` — eight toy specs that build the migration piece by piece. Untracked.
