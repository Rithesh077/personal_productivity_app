# Roadmap

*"Does this reduce the friction in my day?"* replaced *"did I do everything I planned?"* on 26 Jul 2026 (ADR-017). Background in [VISION.md](./VISION.md).

Reorganised 3 Aug 2026 for the React + FastAPI + Rust registry structure (ADR-025). Phases 1–2 completed 10 Aug 2026.

One module at a time. The long-term vision does not block the next useful feature.

## Phase 0: close out the Flet branch

- [ ] Export whatever is in the deployed PWA's localStorage. Once Pages goes, it is gone.
- [ ] Fix the four `page.run_task` calls that sit outside the storage lock: [task_list_analytics.py:268](../src/views/task_list_analytics.py#L268), [:277](../src/views/task_list_analytics.py#L277), [:298](../src/views/task_list_analytics.py#L298), [analytics.py:446](../src/views/analytics.py#L446). Three are reads; `:277` is a write. The branch name claims this work is finished and it is not.
- [x] Read the codebase end to end. The Python is the specification for everything that follows.
- [x] Set up directory scaffold: `frontend/`, `backend/`, `registry/`, `scripts/`.
- [x] Document the restructure: ADR-025 (React + FastAPI), ADR-026 (SQLite triggers), ADR-027 (PWA continuity).

## Phase 1: Python backend (FastAPI + SQLite)

Port the Flet logic into a clean API. The Flet PWA stays deployed (ADR-027) — this phase builds the replacement, not yet ships it.

- [x] FastAPI app scaffold (`backend/app/main.py`, CORS, lifespan)
- [x] Port `models/goal.py` and `models/task_item.py` into `backend/app/models/`
- [x] Port `utils/time_utils.py` and `utils/math_utils.py` into `backend/app/utils/`
- [x] SQLite schema: `goals`, `tasks`, `subtasks`, `task_list_items`, `custom_tags`, `schema_version`
- [x] SQLite triggers for cascading completion (ADR-026)
- [x] Route: `/api/goals` CRUD (create, read, update, delete)
- [x] Route: `/api/goals/{id}/tasks` and subtask nesting
- [x] Route: `/api/task-list` CRUD + reorder + complete
- [x] Route: `/api/analytics/goals` and `/api/analytics/task-list`
- [x] Route: `/api/tags`
- [ ] Port the 67 tests to test models, utils, and the SQLite-backed cascade

## Phase 2: React frontend

Build the UI. Vite dev server proxies `/api` to the Python backend.

- [x] Vite + React scaffold
- [x] Design system: `tokens.css` (colors, spacing, typography from `constants/design.py`)
- [x] Component: GoalCard (hierarchical, expandable, inline edit)
- [x] Component: GoalWizard (multi-step creation flow)
- [x] Component: TaskListCard (priority queue item)
- [x] Component: StatCard and AnalyticsCharts
- [x] Page: Planner (goals list, wizard, CRUD)
- [x] Page: TaskList (priority queue, DMN rescue)
- [x] Page: Analytics (stats, charts, completion history)
- [x] Navigation bar, routing, responsive layout
- [x] Feature parity with Flet PWA confirmed

## Phase 3: cutover

- [x] Data migration: `scripts/migrate_data.py` (localStorage JSON → SQLite)
- [x] Switch daily use from Flet PWA to React + FastAPI
- [ ] Update GitHub Actions to deploy the React app (or retire Pages)
- [x] Mark `src/` as archived

## Phase 4: Rust registry (independent track)

Runs in parallel with phases 1–3. No dependency on the frontend or backend.

- [ ] Toy 1: task list CLI, std only → `core::model` concepts
- [ ] Toy 2: persistence and errors → `core::store` concepts
- [ ] Toy 3: hierarchy and cascading → borrow checker properly
- [ ] Toy 5: registry and crypto → the actual registry
- [ ] `registry/` crate: KDF (Argon2), AEAD (ChaCha20-Poly1305), key hierarchy, encrypted storage
- [ ] Logbook: entries, retrieval, search
- [ ] Keys: password storage, 2FA on writes
- [ ] Auto-relock on timeout

## Phase 5: Tauri integration

- [ ] Tauri v2 shell: wrap the React frontend in a desktop webview
- [ ] Wire `registry/` crate as Tauri commands (`invoke("unlock_logbook", ...)`)
- [ ] Bundle Python backend as a Tauri sidecar process
- [ ] Desktop packaging (Linux, macOS)

## Phase 6: reach

- [ ] Mobile: Tauri v2 mobile targets (logbook reading, keys access)
- [ ] Sync spike: device-to-device, offline-only (ADR-022). The highest-risk item in the project

## Phase 7: the engine

- [ ] Capture and index study material
- [ ] Resource context: which textbook, and how far into it I am
- [ ] Triggers and reminders attached to material rather than dates
- [ ] Dead-time rescue: given ten idle minutes, what to open
- [ ] Exam preparation tracked across months (ISI, JAM, ISS)
- [ ] Local AI over journal and activity data (ADR-023)
- [ ] Browser autofill

## Deferred

Set aside deliberately. Reasoning in [VISION.md](./VISION.md).

- Local AI that reads the whole device and proposes a reorganisation plan. Too much for now
- Offline password reset. Genuinely unsolved (ADR-020)
- Splitting into separate apps and repositories per device. Cheap later, provided ADR-018 holds
- Renaming. After the modules exist, not before

## Carried over from the Flet era

Still wanted, but each gets re-judged against the new stack rather than implemented on the strength of being on an old list.

- [ ] Recurring tasks
- [ ] Variable task duration and time blocks
- [ ] Week view
- [ ] Big-rock prioritisation
- [ ] Automatic rescheduling for missed tasks
- [ ] Focus mode integration
- [ ] Energy-level scheduling
- [x] Priority list / DMN rescue. Shipped in Flet, porting to React
- [x] Concurrency fix. Shipped in Flet, replaced by SQLite transactions + triggers
- [ ] Time analytics. Completion, on-time and same-day exist. Planned versus actual *time*, and most productive day, do not

## Dead

- `views/analytics.py`. 507 lines, fully built, never wired up (ADR-013). Port the metrics, not the view code
- TUI as interim frontend. Replaced by React (ADR-025 amends ADR-021)
