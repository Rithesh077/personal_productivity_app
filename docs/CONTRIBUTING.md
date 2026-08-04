# Contributing to Stride

> Stride is a personal productivity system. This document explains the project structure and development workflow for anyone reviewing the codebase (or future me).

## Current state

The project is mid-migration (ADR-025). Three pieces exist or will exist:

| Directory | Language | Status | Purpose |
|-----------|----------|--------|---------|
| `src/` | Python (Flet) | **Legacy, deployed** | The current PWA. Stays until React reaches parity |
| `frontend/` | React (Vite) | **Scaffolded** | The new UI |
| `backend/` | Python (FastAPI) | **Scaffolded** | REST API + SQLite storage |
| `registry/` | Rust | **Scaffolded** | Encrypted storage (keys + logbook) |

## Prerequisites

- **Python 3.11+**
- **[uv](https://docs.astral.sh/uv/)** — fast Python package manager
- **Node.js 20+** and **npm** (for the React frontend)
- **Rust** (for the registry crate, when you reach it)

## Setup

### Legacy Flet PWA (still deployed)

```bash
uv sync
uv run flet run --web     # web
uv run flet run            # desktop
uv run pytest tests/ -v   # tests
```

### New stack (when scaffolded)

```bash
# both at once
./scripts/dev.sh

# or separately:
cd backend && uvicorn app.main:app --reload --port 8000
cd frontend && npm run dev
```

## Project Structure

```
personal_app/
│
├── frontend/               # React + Vite (new UI)
│   ├── src/
│   │   ├── components/     # GoalCard, GoalWizard, TaskListCard, StatCard
│   │   ├── pages/          # Planner, TaskList, Analytics
│   │   ├── hooks/          # useApi
│   │   ├── services/       # api.js (endpoint definitions)
│   │   └── styles/         # tokens.css, per-component styles
│   └── package.json
│
├── backend/                # Python + FastAPI (new API)
│   ├── app/
│   │   ├── routes/         # goals, tasks, analytics
│   │   ├── models/         # Goal, Task, SubTask, TaskItem
│   │   ├── services/       # SQLite CRUD
│   │   └── utils/          # time, math helpers
│   ├── tests/
│   └── pyproject.toml
│
├── registry/               # Rust crate (keys + logbook)
│   ├── src/                # lib, crypto, keys/, logbook/, store, error
│   └── Cargo.toml
│
├── src/                    # LEGACY: Flet PWA (still deployed)
│   ├── main.py             # entry point, navigation, routing
│   ├── models/             # Goal, Task, SubTask, TaskItem
│   ├── views/              # planner, task list, analytics
│   ├── components/         # goal card, wizard, task list card
│   ├── services/storage.py # SharedPreferences CRUD + schema versioning
│   ├── constants/design.py # design tokens
│   └── utils/              # time, color, math helpers
│
├── tests/                  # LEGACY: tests for src/ (67 tests, pytest)
├── scripts/
│   └── dev.sh              # starts frontend + backend together
├── docs/                   # ADR, vision, roadmap, learning, contributing
└── local/                  # JDs, rust-toys specs (untracked)
```

## Testing

### Legacy tests (src/)

```bash
uv run pytest tests/ -v
```

Tests cover:
- **Models** — serialization roundtrips, completion logic, backwards compatibility
- **Utilities** — time calculations, math helpers, color mappings

### Backend tests (when ready)

```bash
cd backend && uv run pytest tests/ -v
```

Will cover:
- **Models** — same as above, ported
- **SQLite triggers** — cascade completion verified by inserting data and checking outcomes
- **Routes** — API endpoint integration tests

## Architecture Decisions

See [ADR.md](./ADR.md) for the complete record. Key recent decisions:

| ADR | Decision |
|-----|----------|
| ADR-025 | React + FastAPI + Rust registry, Python as future Tauri sidecar |
| ADR-026 | SQLite triggers for cascading completion |
| ADR-027 | Flet PWA stays until React reaches parity |
| ADR-019 | SQLite replaces SharedPreferences |
| ADR-020 | Registry: two-key hierarchy, master password, offline only |

## Key Design Principles

1. **Privacy-first** — Zero cloud, all data local (browser localStorage now, SQLite next)
2. **Personal-first** — Built for one user (the author), not hypothetical users
3. **Accountability-focused** — Core question: "Did I do what I planned?"
4. **Learning counts** — A substantial part of the point is learning properly (ADR-024)

## Storage

### Legacy (src/)

Data is stored in browser `localStorage` via Flet's `SharedPreferences`:

| Key | Contents |
|-----|----------|
| `stride.goals` | All goals as JSON array |
| `stride.schema_version` | Current schema version (for migrations) |
| `stride.task_list` | Active priority task list items |
| `stride.task_list_completed` | Completed task list items |
| `stride.custom_tags` | User-created custom tags |

### New (backend/)

SQLite with normalized tables: `goals`, `tasks`, `subtasks`, `task_list_items`, `custom_tags`, `schema_version`. Cascading completion handled by triggers (ADR-026). Schema in ADR.md.

### Registry (registry/)

Encrypted file. Argon2 KDF, ChaCha20-Poly1305 AEAD. Two independent unlock states (logbook and keys) off one master password. Design in ADR-020.

## Deployment

### Current

Deploys automatically to GitHub Pages on push to `main` via the [deploy workflow](../.github/workflows/deploy.yml). Targets the Flet PWA in `src/`.

### Future

To be decided when the React frontend reaches parity. Options: continue with GitHub Pages (targeting `frontend/dist/`), or retire Pages entirely in favor of a Tauri desktop app.
