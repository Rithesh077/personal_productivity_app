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
Jun 7, 2026  Task List feature implementation
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

*Last updated: Jun 8, 2026*
