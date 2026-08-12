# Architecture Decision Records (ADR)

> A living record of every significant architectural decision in Stride, from first commit to current state.
> Each decision is documented with context, rationale, and consequences.

---

## Timeline Overview

```
Jul 2025     Flask REST API prototype
Aug 2025     FastAPI rewrite + HTML/CSS/JS frontend
Sep 2025     Frontend integration + schedule management
Oct 2025     CLI app for terminal-based task management
Nov 2025     CLI bug fixes (last pre-pivot work)
                ── 5 month gap ──
Apr 2, 2026  Nuclear rewrite: Flet PWA (everything deleted)
Apr 7, 2026  Version 1.0: MVP with full feature set
Apr 14, 2026 GitHub Pages deployment + CI/CD
Apr 19, 2026 UI/UX polish pass
Jun 7, 2026  Task List feature design
Jun 8, 2026  Concurrency lock (RMW hazard fix)
Jul 26, 2026 Second pivot: Tauri + Rust, widened philosophy
Aug 3, 2026  Third restructure: React + FastAPI + Rust registry (current)
```

---

## ADR-001: Project Purpose — Personal-First Philosophy

**Date:** Jul 2025 (formalized Apr 2026)
**Status:** Active

### Context
The project started as a personal productivity app. The core question it answers:
> *"Did I actually do what I planned?"*

### Decision
Build exclusively for a single user (the author). No multi-user support, no authentication, no social features. Every feature must serve the author's actual daily workflow.

### Rationale
- Building for yourself eliminates the trap of designing for hypothetical users
- Forces honest feature prioritization: if *you* won't use it, don't build it
- Removes backend complexity (auth, user management, data isolation)

### Consequences
- The app is maximally simple architecturally
- Every feature can be evaluated against one metric: "does this help ME?"
- Cross-device sync requires creative solutions (no user accounts)

---

## ADR-002: Exploration Phase — Flask → FastAPI → CLI

**Date:** Jul 2025 – Nov 2025
**Status:** Superseded by ADR-003

### Context
The project went through three distinct backend approaches, each a genuine exploration of different paradigms:

**Phase 1: Flask REST API** (Jul – Aug 2025)
- Simple REST API with in-memory feature list
- Endpoints: `GET /`, `GET /features/`, `GET /features/{id}`
- **Learning:** Basic REST API design, Flask routing

**Phase 2: FastAPI + Frontend** (Aug – Sep 2025)
- Migrated to FastAPI for better type safety (Pydantic models)
- Added CORS middleware, POST endpoints, schedule management
- Built vanilla HTML/CSS/JS frontend to consume the API
- **Learning:** API design with validation, frontend-backend integration, CORS

**Phase 3: CLI App** (Oct – Nov 2025)
- Built a terminal-based task manager with JSON file storage
- Priority-based sorting, schedule generation from tasks
- Structured with models/ and utils/ directories
- **Learning:** CLI UX, file-based persistence, priority scheduling

### Decision
Each phase was kept and iterated on until the next approach felt more appropriate. The exploration was deliberate — trying different paradigms to find the right fit for a personal productivity tool.

### Rationale
- Flask was too minimal for structured data
- FastAPI was better but maintaining separate frontend + backend felt heavy for a one-person app
- CLI was fun but lacked visual feedback and couldn't run on mobile

### Consequences
- Built genuine familiarity with Flask, FastAPI, Pydantic, vanilla frontend, CLI design
- All three approaches were eventually deleted in the Flet pivot
- The CLI app's priority sorting concept directly influenced later features

---

## ADR-003: The Flet Pivot — Nuclear Rewrite

**Date:** Apr 2, 2026
**Status:** Active
**Commit:** `6fb2795` (+1866 lines, –453 lines)

### Context
After 5 months away from the project, the author returned with a clear need: a cross-platform app (web + desktop + mobile) from a single Python codebase. Maintaining separate frontend/backend was too heavy for a personal tool.

### Decision
Delete all existing code (Flask backend, FastAPI backend, CLI app, HTML/CSS/JS frontend) and rewrite everything using [Flet](https://flet.dev) — a Python framework that compiles to web, desktop, and mobile from one codebase.

### Rationale
- **Single codebase, all platforms:** Flet renders to Flutter under the hood, giving native-feeling apps on web, desktop, and mobile
- **Python-only:** No JavaScript, no HTML, no CSS — the entire app is Python
- **PWA support built-in:** Flet generates installable PWAs with offline support
- **No backend needed:** Client-side storage (SharedPreferences/localStorage) eliminates server costs and privacy concerns

### AI Collaboration
Architecture and code review were done by the author. Claude Opus helped with coding and Flet API documentation lookups. The co-author tag on the commit (`Co-authored-by: Copilot`) was auto-added by GitHub and is inaccurate — the collaboration was with Claude, not Copilot.

### Consequences
- Entire codebase is now Python (~2500 lines)
- Zero hosting cost (static files on GitHub Pages)
- Lost the schedule management backend — Stride became a goal tracker, not a scheduler
- The original vision (productivity schedule manager) diverged from what was built (goal execution tracker)

---

## ADR-004: Data Model — 3-Level Goal Hierarchy

**Date:** Apr 2, 2026
**Status:** Active

### Context
Needed a way to represent structured work that goes beyond flat task lists.

### Decision
Design a 3-level hierarchy from the start: **Goal → Task → SubTask**

```
Goal: "Launch MVP"
├── Task: "Build authentication"
│   ├── SubTask: "Set up JWT tokens"
│   └── SubTask: "Build login page"
├── Task: "Deploy to production"
│   ├── SubTask: "Configure CI/CD"
│   └── SubTask: "Set up domain"
```

### Rationale
- Goals represent outcomes ("what do I want to achieve?")
- Tasks represent work streams ("what major things do I need to do?")
- SubTasks represent atomic actions ("what's the next concrete step?")
- This maps to how the author naturally thinks about work

### Consequences
- Completion logic cascades: completing all SubTasks auto-completes the Task, completing all Tasks auto-completes the Goal
- Uncompleting a child un-completes the parent chain
- Analytics can report at each level independently (goal completion %, task completion %, subtask completion %)

---

## ADR-005: Privacy-First, Zero-Backend Architecture

**Date:** Apr 2, 2026
**Status:** Active

### Context
A personal productivity tool handles sensitive data (goals, habits, productivity patterns). The author consciously decided against any backend.

### Decision
All data lives in the browser via Flet's SharedPreferences (which maps to localStorage on web). Zero network requests, zero server, zero accounts.

### Rationale
- **Privacy:** No data leaves the device
- **Cost:** $0 hosting (GitHub Pages serves static files)
- **Simplicity:** No backend to maintain, no database to manage, no auth to implement
- **Offline:** Works without internet after first load (PWA)
- **Speed:** No network latency, instant read/write

### Tradeoffs Accepted
- No cross-device sync (data is trapped in one browser)
- No backup/restore (clear browser data = lose everything)
- localStorage has a ~5-10MB limit (sufficient for text-based goal data)

---

## ADR-006: SharedPreferences as Storage Layer

**Date:** Apr 2, 2026
**Status:** Active

### Context
Flet offers several storage options. Needed the simplest one that works across web + desktop.

### Decision
Use `ft.SharedPreferences` for all persistent storage. Data is serialized as JSON strings under namespaced keys (`stride.goals`, `stride.schema_version`).

### Rationale
- Simplest API that works identically on web (localStorage) and desktop (platform preferences)
- JSON serialization is human-readable and debuggable
- No additional dependencies

### Alternatives Considered
- **IndexedDB:** More powerful but Flet doesn't expose it directly
- **SQLite:** Available on desktop/mobile but not on web
- **File storage:** Desktop-only, not available on web

---

## ADR-007: Schema Versioning — Proactive Migration System

**Date:** Apr 2, 2026
**Status:** Active

### Context
Client-side storage is fragile. App updates can change the data shape, breaking deserialization of existing user data.

### Decision
Built a schema versioning system proactively, before any schema changes occurred:
- `stride.schema_version` key tracks the current schema version
- On app load, `_run_migrations()` checks the stored version against `SCHEMA_VERSION`
- Additive changes (new fields) need no migration — `from_dict()` handles missing fields with defaults
- Destructive changes (renames, type changes) get explicit migration blocks
- Migration only runs once per session (cached with `_migration_done` flag)

### Rationale
- The author anticipated the data model would evolve
- Losing user data to a schema change is unacceptable for a personal tool
- Better to build the migration framework early than retrofit it after data loss

### Consequences
- Backwards compatibility is maintained: old key `steps` still deserializes to `sub_tasks`
- New fields can be added to models without any migration code
- The framework is ready for future breaking changes

---

## ADR-008: Default 24-Hour Deadline

**Date:** Apr 7, 2026 (v1.0)
**Status:** Active

### Context
Most task apps default to "no deadline." This means analytics about on-time completion have no baseline.

### Decision
Every goal gets a deadline. If the user doesn't set a custom one, it defaults to **24 hours from creation**.

### Rationale
- Analytics always have data: "same-day execution" metric requires knowing when something was created
- Forces a sense of urgency: "you said you'd do this — did you do it within 24 hours?"
- Aligns with the core philosophy: *"Did I do what I planned?"* requires a time frame to judge against
- Custom deadlines are available for goals that genuinely need longer timeframes

### Consequences
- The analytics distinguish between "on-time" (custom deadline met) and "same-day" (default 24h met)
- Users who create goals and forget about them will see them marked as "overdue"
- This is a feature, not a bug — it creates honest accountability

---

## ADR-009: Notion-Style Inline Editing

**Date:** Apr 7, 2026 (v1.0)
**Status:** Active

### Context
Traditional CRUD apps use forms or modals for editing. This feels heavy for quick title changes.

### Decision
Implement tap-to-edit inline text editing inspired by Notion's block editor:
- Titles are displayed as text
- Tapping converts them to an input field in-place
- Enter saves, clicking away saves, cancel button discards
- No modal, no navigation — edit happens right where the content lives

### Rationale
- Reduces friction for the most common edit operation (renaming)
- Feels modern and responsive
- Keeps the user in context — no disorienting modal transitions

---

## ADR-010: Design System with Tokens

**Date:** Apr 7, 2026 (v1.0)
**Status:** Active

### Context
UI consistency requires centralized design values.

### Decision
Create a design token system in `constants/design.py`:
- Colors: `TEAL`, `AMBER`, `RED`, `PURPLE`, `MUTED`
- Backgrounds: `BG`, `CARD_BG`, `SURFACE`
- Text: `TEXT_PRIMARY`, `TEXT_SECONDARY`, `TEXT_MUTED`
- Layout: chart heights, bar sizes, truncation limits

### Rationale
- Single source of truth for all visual values
- Easy to theme or adjust globally
- Prevents color/spacing drift across components

---

## ADR-011: Cascading Completion Logic

**Date:** Apr 7, 2026 (v1.0)
**Status:** Active

### Context
In a 3-level hierarchy, completion state needs to flow correctly.

### Decision
- **Downward cascade:** Completing a Task marks all its SubTasks complete. Completing a Goal marks all Tasks and SubTasks complete.
- **Upward auto-complete:** When all SubTasks in a Task are checked, the Task auto-completes. When all Tasks in a Goal are checked, the Goal auto-completes.
- **Upward un-complete:** Unchecking any child un-completes the parent chain.
- **Deletion re-evaluation:** Deleting a child triggers re-check — if remaining siblings are all complete, parent stays complete.

### Rationale
- Matches natural mental model: "if all parts are done, the whole is done"
- Prevents stale state where a Goal shows "incomplete" even though everything inside is done

---

## ADR-012: GitHub Pages Deployment via Flet Publish

**Date:** Apr 14, 2026
**Status:** Active

### Context
Needed to deploy the PWA publicly for access from any device.

### Decision
Use `flet publish` to build static web assets, deploy to GitHub Pages via GitHub Actions.

### Pipeline
1. Push to `main` triggers workflow
2. `flet publish src/main.py --base-url /Stride/` builds static files
3. Upload `src/dist/` as Pages artifact
4. Deploy to `https://rithesh077.github.io/Stride/`

### Consequences
- Zero-cost deployment
- Automatic deploys on every push to main
- No server to maintain
- PWA is installable from the deployed URL

---

## ADR-013: Analytics View — Built but Gated

**Date:** Apr 14, 2026
**Status:** Active (analytics still shows "Coming Soon" in nav)

### Context
The analytics view (`views/analytics.py`) was fully implemented with:
- Completion by level (goal/task/subtask)
- Status distribution (active/completed/overdue)
- On-time analysis, same-day execution metrics
- Recent goals progress bars
- Completion history with badges

However, the author was still iterating on the analytics and didn't consider it ready for daily use.

### Decision
Keep the analytics tab wired to a "Coming Soon" placeholder in `main.py`, even though the full implementation exists. Ship it when it's ready.

### Rationale
- Analytics on incomplete data can be misleading
- The author wanted to use the planner for a while first to generate meaningful data before exposing analytics
- Better to gate incomplete features than ship something half-baked

---

## ADR-014: Original Vision vs. What Was Built

**Date:** Jun 7, 2026 (documented retrospectively)
**Status:** Acknowledged

### Context
The `productivity schedule manager.txt` was written **before** the Flet pivot as the original product vision. It describes a time-block schedule manager with features like:
- Recurring tasks on a calendar
- Variable task durations with visual time blocks
- Conflict detection for double-booked slots
- Week view calendar
- Focus mode integration
- Energy-level scheduling

What was actually built is a **goal execution tracker** — a hierarchical task manager that tracks whether you completed what you planned, not a calendar/scheduler.

### Decision
Acknowledge the divergence. The spec and the app are fundamentally different products. The app answers "Did I do what I planned?" while the spec describes "When should I do things?"

### Rationale
During the Flet pivot, the author focused on the core philosophy ("Did I do what I planned?") rather than the spec's calendar-based features. The goal hierarchy + analytics combination directly serves this philosophy. The spec's features (recurring tasks, time blocks, conflict detection) serve a different question ("How should I organize my time?").

### Consequences
- Tier 1-3 features from the spec are mostly unimplemented (0.5/11)
- The app has strong features NOT in the spec (hierarchy, inline editing, undo, cascading completion)
- Future development will evaluate spec features against the core philosophy rather than implementing them blindly

---

## ADR-015: Priority Tasks List — DMN Rescue Queue

**Date:** Jun 7, 2026
**Status:** Implemented

### Context
The author identified a friction point in daily productivity: when encountering time-wasting activities (scrolling, default mode network), there's no quick way to pull a pre-prioritized task and start working on it immediately.

### Decision
Build a **Task List** — an ordered list of immediate tasks that can be pulled from when the author needs to redirect attention.

### Design Decisions (from clarification sessions)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Navigation** | New third tab: Planner \| Task List \| Analytics | Keeps it at the same level as Planner, always one tap away |
| **Item entity** | New standalone entity, optionally linked to Goals | Decoupled from goal hierarchy — task list items are about "right now," goals are about outcomes |
| **Fields** | Title + optional description + tags (hybrid predefined + custom) | Rich enough to categorize, simple enough to add in seconds |
| **Tags** | Predefined defaults (learning, bug, admin, creative, health, urgent) + custom | Hybrid gives structure without rigidity |
| **Reorder** | Flet drag-and-drop (LongPressDraggable) | Direct manipulation feels natural for priority ordering |
| **Add position** | Visual "insert here" tap-targets between items | More intuitive than abstract position numbers |
| **Visual ordering** | No index numbers, position 0 highlighted with special "NEXT UP" card | Reduces visual noise, emphasizes what matters |
| **Completion** | Checkmark on any item, confirmation dialog | Prevents accidental completion, allows out-of-order completion |
| **After completion** | Moves to completed history, integrated in Analytics tab | Completed items contribute to analytics, don't clutter the active list |
| **Queue size** | Unlimited | Author manages their own discipline |
| **Goal linking** | Subtle dropdown to pick from existing goals | Optional connection without forced coupling |
| **Completed items** | Kept with user-clearable setting | User controls their own data retention |
| **Add UI** | Mobile + desktop compatible (Flet responsive) | Must work on both phone and laptop |
| **Analytics** | Only task list analytics for now | Don't ship half-built analytics, iterate focused |

### Consequences
- New data model (`TaskItem`) with its own storage keys (`stride.task_list`, `stride.task_list_completed`)
- New view (`task_list.py`), new component (`task_list_card.py`), new nav tab
- Analytics tab evolves from "Coming Soon" to task list completion history
- First feature built with mobile-first responsive design considerations

---

## ADR-016: Concurrency Control — Resolving RMW Hazards

**Date:** Jun 8, 2026
**Status:** Implemented

### Context
When a user interacted with the UI rapidly (e.g., clicking multiple subtask checkboxes in under 100ms), Flet spawned multiple concurrent background tasks. Because the storage layer loads the entire hierarchical JSON, modifies it, and saves it back, this created a classic **Read-Modify-Write (RMW) hazard**. Task B would read the state before Task A saved, and Task B's save would overwrite Task A's modification.

### Decision
Implemented a global `asyncio.Lock()` (Mutex) at the storage layer (`storage.py`) and a `run_locked_task()` wrapper. All UI-triggered background tasks that read or write state are now executed through this locked wrapper.

### Rationale
- **Alternative 1 (Normalization):** Flattening the database into separate tables solves some overwrite issues, but cascading logic (subtask completion triggering task completion) still requires locking to prevent race conditions during parent state evaluation.
- **Alternative 2 (Optimistic UI + Event Queue):** Tracking temporary state locally and queueing background saves is robust but significantly increases architectural complexity for a zero-backend PWA.
- **Chosen Solution (`asyncio.Lock`):** Since Flet runs its async tasks on a single asyncio event loop, a standard mutex forces all rapid clicks to execute their read-modify-write cycles sequentially. It's simple, native to Python, and completely eliminates the data loss hazard without changing the underlying JSON schema.

### Consequences
- UI interactions that trigger storage writes are now strictly serialized.
- Zero risk of dropped clicks or state overwrites.
- Replaced `page.run_task(handler)` with `run_locked_task(page, handler)` across the planner and task list views.

---

## ADR-017: The Second Pivot, Tauri and Rust

**Date:** Jul 26, 2026
**Status:** Active
**Supersedes:** ADR-003. Amends ADR-001

### Context

Two separate things changed at the same time, and it's worth keeping them apart:

1. A framework migration. Off Flet and Python, onto Tauri with a Rust core.
2. A product change. The philosophy widens past *"did I do what I planned?"*

They happened together so they're recorded together, but either could have happened without the other.

### Decision

Rewrite in Rust, ship through Tauri.

On the product side, the question becomes *"does this make my day less annoying?"*. The old question survives as the planner module's job. Three larger modules join it (vault + journal, the intelligence engine, sync) and once those land the goal tracker becomes a subordinate piece. Detail in [VISION.md](./VISION.md).

### Rationale

Why Rust, honestly: to learn it properly from the ground up. That's a stated project goal, not a side effect (ADR-024). My background is C, so manual memory management isn't new territory, and Rust is the obvious next step rather than a leap.

Why Tauri:
- A native desktop app with an actual systems language underneath, which Flet couldn't give me
- Tauri v2 targets mobile, so the cross-platform reach that motivated ADR-003 survives
- Small binaries, uses the OS webview instead of shipping a browser engine
- Direct filesystem, SQLite and keychain access, all of which the vault needs and a browser sandbox won't allow

Why the philosophy widened: I've barely used the app and I still prefer paper. What it *did* turn out to be good for was analysing what I'd been doing. So rather than keep polishing a goal tracker that loses to a notebook on capture speed, move toward what software is actually better at, which is retrieval, persistence, and looking across long stretches of time.

### Consequences

- The Python `src/` tree, about 2900 lines, becomes reference material. The 67 passing tests document intended behaviour and should be ported to Rust rather than deleted.
- The PWA dies. GitHub Pages deployment ends with the migration, so ADR-012 is terminal. That's a real loss of cross-device access, and it's why sync gets promoted to a headline feature in ADR-022.
- The migration runs through eight toy projects, each producing a module the real app keeps. Specs in `local/rust-toys/`.
- The name doesn't change for now. That's a deliberate deferral, not an oversight.

---

## ADR-018: Core-First Workspace Layout

**Date:** Jul 26, 2026
**Status:** Active

### Context

I might split this into several apps or repos later, one per device scope. My words at the time were "how hard can copy pasting and rewiring the code be right?......right?"

The honest answer is that it's trivial if the core has no UI dependencies and awful if it does. The current Flet app is the proof: business logic and layout are tangled together throughout `planner.py`, all 662 lines of it, so nothing can be lifted out without a rewrite.

### Decision

A Cargo workspace with a core crate that has no UI in it.

```
core/     models, storage, planner logic, vault, sync. no UI deps
tui/      ratatui frontend, consumes core
desktop/  Tauri app, consumes core
mobile/   later, consumes core
```

Every frontend is a consumer of `core`. `core` never knows a frontend exists.

### Rationale

- Reduces the future split to moving a directory rather than untangling a codebase
- `core` becomes testable without a UI, which the Flet views never were
- The TUI and Tauri can both exist during the transition (ADR-021) instead of one blocking the other
- It forces honest interface design. If `core` needs to ask me something, that is a return value, not a dialog box

### Consequences

- A bit more ceremony up front: workspace manifests, explicit crate boundaries
- Any UI concern that leaks into `core` is a bug to fix immediately, not a shortcut to live with
- Toys 1 to 5 build `core` modules, toys 6 and 7 build consumers. The curriculum and the architecture are deliberately the same shape

---

## ADR-019: SQLite Replaces SharedPreferences

**Date:** Jul 26, 2026
**Status:** Active
**Supersedes:** ADR-006

### Context

ADR-006 picked SharedPreferences (a JSON blob in localStorage) because it was the simplest thing that worked on both web and desktop in Flet. It came with known costs: a 5 to 10MB ceiling, a full blob rewrite on every change, and the read-modify-write hazard ADR-016 had to fix with a mutex.

The new modules break all of those assumptions. Journals, indexed study material and encrypted secrets are neither small nor happy being rewritten wholesale.

### Decision

SQLite for everything, with the constraint that the data stays portable. A file I can copy, back up and move between devices.

### Rationale

- Real queries, which the intelligence engine needs and a JSON blob can't do
- Partial writes and transactions, so a whole class of RMW hazard stops existing at the storage layer
- One portable file, which is exactly the SSD-death scenario from VISION.md
- Well proven, and a decent way to learn how databases work from underneath
- Encrypted blobs sit in it fine, so the vault composes without a fight

### Alternatives Considered

JSON files. Simplest, but no queries and the same blob rewrite problem. Rejected.

A hand-rolled storage engine. Genuinely tempting given the learning goal and consistent with the no-imports instinct, but rejected on scope. That effort is better spent on the vault and on sync, which are the parts nobody else can build for this project.

### Consequences

- Schema migrations become real migrations. The ADR-007 framework was never actually exercised
- Sync semantics have to be decided at row level rather than blob level, which is harder but is the right problem (ADR-022)
- The ADR-016 `asyncio.Lock` has no direct successor. SQLite transactions plus `Arc<Mutex>` cover it, and the compiler refuses the shared-mutable-state bug outright

---

## ADR-020: Vault Architecture

**Date:** Jul 26, 2026
**Status:** Active. Design settled, some mechanics still open

### Context

The vault and journal are the main thing. The scenario driving it is specific: the laptop dies, the SSD corrupts, and I lose passwords and context and spend weeks rebuilding. The vault exists so that stops being possible.

### Threat model

What I'm defending against, in order:

1. Someone with the disk, or the backup, or the synced copy. This is the main one, because sync means encrypted data will deliberately be sitting on more than one device.
2. Casual access to an unlocked machine. Hence auto-relock and the separate journal unlock state.
3. Interception during device-to-device sync.

Not defending against a compromised OS with a kernel-level keylogger. Out of scope for a personal app.

### Decision

Two independent unlock states, off one master password:

```
master password --KDF--> master key
                            |-> journal key   (unlocks the journal)
                            |-> secrets key   (unlocks passwords/2FA)
```

Unlocking the journal must not unlock the secrets vault. Reading yesterday's entry over lunch is a different act from opening the password store and the app should treat it that way.

Rules:
- Master password on every launch. No "remember me"
- 2FA to change a password, not to read one. Writing is the higher bar
- Auto-relock on a timeout
- Everything offline. No cloud, no accounts, no recovery server
- Browser autofill later, as its own piece of work with its own attack surface

### Rationale

Two keys instead of one because the two data sets have genuinely different exposure and access patterns. With one key, every casual journal read hands over full password access, which is a bad trade for a convenience I never asked for.

This is also the one place where the hand-roll-by-default instinct gets overridden. Cryptographic primitives come from audited crates: Argon2 for key derivation, an AEAD like ChaCha20-Poly1305 or AES-GCM, plus something to zero memory. Rolling my own is how personal vaults get quietly broken, and a break here loses precisely the data this app exists to protect. Everything around the primitives (key hierarchy, file format, unlock flow, relock policy) is hand-built, and that's where the learning is anyway.

### Open questions

Offline password reset is unsolved. My sketch was that a reset sends a random number to the app on my phone, which collapses because the phone needs the vault to receive it. Options are printed recovery codes kept physically, secret sharing across devices, or accepting that a forgotten master password means the data is gone. Undecided.

What the second factor physically is, with no server and no cloud. A TOTP seed stored inside the vault is circular. Probably a hardware token or a second enrolled device.

### Consequences

- Two unlock states means two session lifetimes to manage, on every frontend
- Sync moves ciphertext only, and no device should ever hold a decrypted copy in transit
- Losing the master password with no recovery path is currently total loss. Until that open question is settled the UI has to say so loudly

---

## ADR-021: TUI First, React Later

**Date:** Jul 26, 2026
**Status:** Active

### Context

Tauri needs a web frontend. I want React, partly for what it can do and partly because UI design is the break I take from technical work, and I want to learn UI/UX from scratch and design something actually mine. But that design doesn't exist yet, and waiting on it would block every backend module.

### Decision

Ship a TUI as the interim daily driver straight after the migration. Build the Tauri and React shell when there's a design worth building.

Both consume `core` (ADR-018), so this is sequencing, not a fork.

### Rationale

- Unblocks the vault, journal and engine, none of which need a pretty interface to be useful
- A TUI is quick to build, quick to use, and honest about being a tool rather than a product
- Gets the app into actual daily use sooner, which matters given I've barely used the current one
- Takes the pressure off the visual design. The unique UI is supposed to be the fun part, and designing it against a deadline would ruin that
- Terminal-first fits how I work anyway, and it echoes the Oct 2025 CLI phase from ADR-002, which was enjoyable and died for lack of persistence and mobile reach. `core` solves both

### Consequences

- Two frontends to maintain once React lands. Acceptable, since the TUI remains useful over SSH and doubles as a permanent test harness for `core`
- The design tokens from `constants/design.py` (ADR-010) carry over conceptually. Colours and spacing map to both a terminal palette and CSS variables
- Mobile gets neither at first. Mobile arrives with React

---

## ADR-022: Offline-Only Sync

**Date:** Jul 26, 2026
**Status:** Accepted in principle. Design open, feasibility unproven

### Context

ADR-005 accepted no cross-device sync as the price of a zero-backend architecture. That trade doesn't hold any more. The PWA dies with the migration (ADR-017), taking the only cross-device access path with it, and the whole point of the vault is surviving the loss of one machine. Data sitting on one device isn't backed up.

### Decision

Device-to-device sync with no cloud at all. Not cloud-optional, not a self-hosted server, nothing I don't physically own. LAN discovery, direct transfer, or sneakernet.

### Rationale

Non-negotiable one in VISION.md is that it's offline. Syncing ciphertext to a rented box would quietly undo the privacy posture the whole thing is built on.

Beyond that, edge compute, cybersecurity and IoT intersect precisely here, and those are the three areas I am most interested in. I may not succeed at it, and that is accepted going in. It is the highest-risk item in the project, and the reasoning is that the learning pays for itself even if the feature never ships.

### Open questions

- Discovery. mDNS on the LAN, manual pairing with a QR code, or both
- Transport. what provides authenticated encryption between devices, and how devices get enrolled
- Conflict resolution. Journal entries are append-mostly and easy. Vault entries are mutable, and last-write-wins can silently destroy a password change made on another device. CRDTs are the principled answer and a serious undertaking
- Whether a phone with no app installed ever gets read-only access, and how, without a server

### Consequences

- Sync design constrains the SQLite schema (ADR-019). Per-row versioning or vector clocks are far cheaper to design in now than to retrofit
- Scheduled last of the toy projects, because it depends on the vault, the storage layer, and real data existing first
- If it turns out to be infeasible, the fallback is manual encrypted export and import. Worse, but it still covers the SSD-death scenario, which is the actual requirement

---

## ADR-023: Local AI, and Reversing "No AI"

**Date:** Jul 26, 2026
**Status:** Active. Direction set, implementation deferred

### Context

The README has said "No AI" since the Flet rewrite. I've now described the intelligence engine as an engine to replace LLMs from my life, while also saying we'll have local AI. That reads as a contradiction and isn't one.

### Decision

Local AI is in scope. Cloud AI isn't.

The goal is ending my dependence on someone else's LLM service: the round trip, the account, my data leaving the device, the vendor who can change terms or disappear. The model runs on my hardware, over my data, with the network unplugged.

Uses: coding help for assignments, exam prep (ISI, JAM, ISS), and reading my own journal and activity data to put a plan together.

### Rationale

This is consistent with the offline non-negotiable. A local model is actually *more* aligned with the privacy posture than where I am now, where using a cloud LLM means my questions leave the machine entirely.

And the journal and activity data are exactly the context an external model can never have, which is the thing that would make a local one genuinely better rather than just more private.

### Consequences

- The README's "No AI" line is now false and has to be rewritten
- ADR-005's privacy rationale gets stronger, not weaker. Data still never leaves the device
- Model choice and runtime are deferred until there's a corpus worth feeding it. Building inference before there's data is backwards
- The bigger version, a model that reads the whole device and proposes a reorganisation and automation plan, is parked. It's too much right now and I need features that actually help me first. Recorded because it's deliberate, not forgotten

---

## ADR-024: Learning Is a Requirement

**Date:** Jul 26, 2026
**Status:** Active

### Context

Most projects treat "the author learned something" as a nice side effect. Here it carries the same weight as shipping. The pivot to Rust exists substantially so that I learn Rust from the ground up, and so I can build creative solutions and modules instead of calling a billion imports.

### Decision

Learning value is a legitimate tiebreaker when choosing between implementations. Where both a hand-rolled module and a dependency would be reasonable, hand-roll it.

The exception is cryptography. Always audited crates. Getting it wrong loses the data the app exists to protect, and hand-rolling it teaches the wrong lesson anyway.

Secondary exceptions where the wheel isn't worth reinventing: SQLite, the Tauri runtime, serde, and the terminal and rendering backends.

### Working method

- I write the code, test it and refactor it. Assessment comes after. The reverse only happens if I say so
- No unsolicited solutions when I'm stuck. I'll ask
- Explain things through C, which is my strongest language and the right bridge to ownership and lifetimes

### Rationale

Optimising purely for shipping speed means importing something for everything and learning nothing, which leaves me with an app I don't understand well enough to maintain on my own. For a one-person personal tool that's a slow-motion failure. Optimising purely for learning means hand-rolling crypto and losing the vault. The line between the two is drawn above on purpose.

### Consequences

- Development is slower, deliberately
- Every module gets a toy project first (`local/rust-toys/`), each producing code the real app keeps, so the learning detour and the migration are the same path
- Progress is tracked in [LEARNING.md](./LEARNING.md), including which concepts I actually understand versus which ones I've merely used

---

## ADR-025: React + FastAPI, Python as Sidecar

**Date:** Aug 3, 2026
**Status:** Active
**Amends:** ADR-017, ADR-021

### Context

ADR-017 planned a full rewrite: Flet dies, everything gets rebuilt in Rust, TUI ships first, React comes later. That plan was correct in direction but wrong in sequencing. The vault is the hard, new thing that requires learning Rust properly. The UI is the thing I've already built and know how to build. Blocking the UI on learning a new language means neither ships.

### Decision

Split the migration into independent tracks:

1. **React frontend** — replaces the Flet UI. Vite + React. Consumes a REST API.
2. **Python backend** — FastAPI. The existing models, utils, and business logic ported out of Flet views into route handlers. SQLite replaces SharedPreferences.
3. **Rust registry** — standalone crate (`registry/`), built independently as a learning project. Two submodules: `keys` (passwords) and `logbook` (journal).
4. **Tauri shell** (future) — wraps the React frontend, runs the registry as native Rust commands, runs Python as a sidecar process.

The Flet PWA stays deployed and functional until the React frontend reaches parity.

### Rationale

The full-rewrite plan from ADR-017 had two risks:
- Learning Rust and rebuilding the UI at the same time, making both slower
- No usable app for months while the rewrite happens

This restructure lets me:
- Ship a better UI (React) without waiting for Rust
- Learn Rust properly on the registry, which is the actual reason for the pivot
- Keep using the Flet PWA in the meantime
- Connect everything through Tauri when both pieces are ready

ADR-021 (TUI first, React later) is amended: the TUI is no longer the interim frontend. React is. The TUI remains an option as a permanent tool for SSH use but is no longer a prerequisite.

### Consequences

- Three languages in one repo: Python, JavaScript, Rust. Acceptable for a personal project; would need reconsideration if collaborators appeared
- The Python backend eventually becomes a Tauri sidecar, so it needs to run as a standalone process (FastAPI + uvicorn) and accept commands either via HTTP or stdin/stdout
- The Flet `src/` directory stays as reference and active deployment until React has parity
- `scripts/dev.sh` starts both frontend and backend in one command

---

## ADR-026: SQLite Triggers for Cascading Completion

**Date:** Aug 3, 2026
**Status:** Active
**Implements:** ADR-019

### Context

The current cascading completion logic lives in `planner.py` as nested `async def` closures (~200 lines across `toggle_task_async`, `toggle_subtask_async`, `do_delete_task`, `do_delete_subtask`). It's the biggest contributor to the view being a god function.

With the move to SQLite (ADR-019), there's a choice: keep the cascade logic in Python route handlers, or push it into the database as triggers.

### Decision

SQLite triggers handle cascading completion.

```sql
-- when all subtasks of a task are completed, auto-complete the task
CREATE TRIGGER auto_complete_task
AFTER UPDATE OF is_completed ON subtasks
WHEN NEW.is_completed = 1
BEGIN
    UPDATE tasks SET
        is_completed = 1,
        completed_at = datetime('now')
    WHERE id = NEW.task_id
      AND NOT EXISTS (
          SELECT 1 FROM subtasks
          WHERE task_id = NEW.task_id AND is_completed = 0
      );
END;

-- when all tasks of a goal are completed, auto-complete the goal
CREATE TRIGGER auto_complete_goal
AFTER UPDATE OF is_completed ON tasks
WHEN NEW.is_completed = 1
BEGIN
    UPDATE goals SET
        is_completed = 1,
        completed_at = datetime('now')
    WHERE id = NEW.goal_id
      AND NOT EXISTS (
          SELECT 1 FROM tasks
          WHERE goal_id = NEW.goal_id AND is_completed = 0
      );
END;

-- when a subtask is uncompleted, uncomplete its parent task and goal
CREATE TRIGGER uncomplete_task_on_subtask
AFTER UPDATE OF is_completed ON subtasks
WHEN NEW.is_completed = 0
BEGIN
    UPDATE tasks SET is_completed = 0, completed_at = NULL
    WHERE id = NEW.task_id AND is_completed = 1;
END;

CREATE TRIGGER uncomplete_goal_on_task
AFTER UPDATE OF is_completed ON tasks
WHEN NEW.is_completed = 0
BEGIN
    UPDATE goals SET is_completed = 0, completed_at = NULL
    WHERE id = NEW.goal_id AND is_completed = 1;
END;
```

### Rationale

- Moves ~200 lines of the most tangled business logic out of Python entirely
- The cascade becomes testable by inserting data and checking outcomes — no UI, no mocks, no Flet page
- Triggers fire regardless of which code path writes to the database, so the cascade can't be accidentally bypassed (which is exactly the bug class the four unlocked `page.run_task` calls represent)
- It's the honest place for this logic: the cascade is a data integrity constraint, not a UI concern

### Consequences

- Triggers are harder to debug than Python code when they misbehave. SQLite's `RAISE(ABORT, ...)` helps, but it's not a stack trace
- The trigger definitions become part of the schema, versioned and migrated alongside table definitions
- Route handlers become simple: update the row, return the updated goal. The cascade happened already
- The 67 existing tests that verify cascade behavior become integration tests against the database rather than unit tests against Python functions

---

## ADR-027: PWA Continuity

**Date:** Aug 3, 2026
**Status:** Active
**Amends:** ADR-017

### Context

ADR-017 declared the PWA dead. That was premature. The React frontend and Python backend don't exist yet, and killing the only working deployment before replacements are ready means no app at all.

### Decision

The Flet PWA stays deployed on GitHub Pages and remains the daily driver until the React + FastAPI stack reaches feature parity. The `src/` directory, the GitHub Actions workflow, and the pyproject.toml are not deleted or broken.

"Feature parity" means: all three views (planner, task list, analytics) work in the React app, data has been migrated from localStorage to SQLite, and I've switched to using it daily.

### Consequences

- Two working apps will exist in parallel for a while. That's fine — one is legacy, one is next
- The `src/` directory is explicitly labeled as legacy in the README
- No changes are made to `src/` except critical bugfixes (like the four unlocked `page.run_task` calls from ROADMAP Phase 0)
- GitHub Actions deployment continues targeting `src/` until the React app is ready to replace it

---

*Last updated: Aug 4, 2026*
