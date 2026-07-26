# Roadmap

*"Does this reduce the friction in my day?"* replaced *"did I do everything I planned?"* on 26 Jul 2026 (ADR-017). Background in [VISION.md](./VISION.md).

One module at a time. The long-term vision does not block the next useful feature.

Reorganised 26 Jul 2026 for the Tauri pivot.

## Phase 0: before anything breaks

- [ ] Export whatever is in the deployed PWA's localStorage. Once Pages goes, it is gone.
- [ ] Read the codebase end to end. The Python is the specification for the Rust.
- [ ] Close out the current branch. Four `page.run_task` calls still sit outside the storage lock: [task_list_analytics.py:268](../src/views/task_list_analytics.py#L268), [:277](../src/views/task_list_analytics.py#L277), [:298](../src/views/task_list_analytics.py#L298), [analytics.py:446](../src/views/analytics.py#L446). Three are reads; `:277` is a write. Skippable if Flet is being abandoned immediately, but the branch name claims this work is finished and it is not.

## Phase 1: learn the language

Specs in `local/rust-toys/`. Each toy leaves behind a module the real app keeps.

- [ ] Toy 1, task list CLI, std only. Becomes `core::model`
- [ ] Toy 2, persistence and error handling. Becomes `core::store`
- [ ] Toy 3, hierarchy and cascading completion. Becomes `core::planner`. The hard one
- [ ] Toy 4, concurrency and locking. Becomes the storage locking
- [ ] Toy 5, vault and crypto. Becomes `core::vault`. The important one

## Phase 2: migrate

- [ ] Cargo workspace with a UI-free `core` crate (ADR-018)
- [ ] SQLite schema and migrations (ADR-019)
- [ ] Port the goal, task and subtask hierarchy and the cascade (ADR-004, ADR-011)
- [ ] Port the priority list (ADR-015)
- [ ] Port the 67 Python tests. They are the behavioural specification
- [ ] Toy 6, the TUI (ADR-021)

The migration is complete when the TUI has replaced the PWA in daily use, not when it compiles.

## Phase 3: the main thing

- [ ] Vault: master password, key hierarchy, two unlock states (ADR-020)
- [ ] Journal: entries, retrieval, search
- [ ] Secrets: password storage, 2FA on writes
- [ ] Auto-relock on timeout

## Phase 4: reach

- [ ] Toy 7, Tauri shell
- [ ] React frontend, once there is a design worth building (ADR-021)
- [ ] Mobile: journal reading and vault access
- [ ] Toy 8, sync spike (ADR-022). The highest-risk item in the project

## Phase 5: the engine

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

Still wanted, but each gets re-judged against the new philosophy rather than implemented on the strength of being on an old list (ADR-014).

- [ ] Recurring tasks
- [ ] Variable task duration and time blocks
- [ ] Week view
- [ ] Big-rock prioritisation
- [ ] Automatic rescheduling for missed tasks
- [ ] Focus mode integration
- [ ] Energy-level scheduling
- [x] Priority list / DMN rescue. Shipped in Flet, and generalises into the engine's dead-time rescue
- [x] Concurrency fix. Shipped in Flet, and most of the problem stops existing under SQLite and Rust
- [ ] Time analytics. Completion, on-time and same-day exist. Planned versus actual *time*, and most productive day, do not

## Dead

- PWA and GitHub Pages deployment. Ends with the migration (ADR-017). Sync replaces it as the cross-device story
- `views/analytics.py`. 506 lines, fully built, never wired up (ADR-013). Port the metrics, not the view code
