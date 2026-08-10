# Stride

**Plan. Execute. Improve.**

A privacy-first personal system built for exactly one user. It answers one question: _"Does this reduce the friction in my day?"_

No cloud. No accounts. No integrations. All data stays on the device.

---

> ## Project structure
>
> As of **Aug 10, 2026**, Stride is a three-part system:
>
> | Directory | What | Status |
> |-----------|------|--------|
> | `frontend/` | React + Vite UI | **Built** |
> | `backend/` | Python + FastAPI API + SQLite | **Built** |
> | `registry/` | Rust encrypted storage (keys + logbook) | Not started |
> | `src/` | **Legacy** Flet PWA (still deployed, still works) | Active until React has parity |
>
> The Flet PWA stays live on GitHub Pages until the new stack reaches feature parity ([ADR-027](docs/ADR.md)).
>
> Read [VISION.md](docs/VISION.md) for where this is going, and [ADR-025 onward](docs/ADR.md) for the restructure decisions.

---

## Features

### New stack (React + FastAPI)

- **Hierarchical Goals** — Create goals with tasks and sub-tasks, cascading completion via SQLite triggers
- **Priority Task List** — A DMN-rescue queue for immediate, non-nested actions with tags
- **Analytics Dashboard** — Completion rate, on-time %, same-day execution, tag breakdown
- **Multi-step Goal Wizard** — Three-step creation: title → tasks/subtasks → review
- **Inline Editing** — Double-click-to-edit titles, inline add fields
- **Full REST API** — Every mutation returns the full updated Goal for clean state sync
- **Responsive** — Desktop top nav, mobile bottom tab bar

### Legacy (Flet PWA, still deployed)

- Same features as above (except wizard and REST API)
- PWA — add to homescreen, works offline
- Schema versioning — data survives app updates with migration support

## Quick Start

### New stack

```bash
# install dependencies
cd backend && uv sync && cd ..
cd frontend && npm install && cd ..

# run both servers
./scripts/dev.sh

# or separately:
cd backend && uvicorn app.main:app --reload --port 8000
cd frontend && npm run dev     # proxies /api to :8000
```

### Legacy Flet PWA

```bash
uv sync
uv run flet run --web      # web
uv run flet run             # desktop
uv run pytest tests/ -v    # 67 tests
```

## Documentation

| Document | Description |
|----------|-------------|
| [Vision](docs/VISION.md) | What this is becoming, and why |
| [Architecture Decisions](docs/ADR.md) | Every decision, Flask through React + Rust |
| [Roadmap](docs/ROADMAP.md) | What's next, in order |
| [Contributing](docs/CONTRIBUTING.md) | Project structure, setup, testing |
| [Learning](local/rust-toys/LEARNING.md) | The Rust curriculum and progress |

## Project Structure

```
personal_app/
├── frontend/              # React + Vite (UI)
├── backend/               # FastAPI + SQLite (API)
├── registry/              # Rust crate (keys + logbook) — not started
├── src/                   # LEGACY: Flet PWA (deployed, active)
├── tests/                 # LEGACY: pytest (67 tests for src/)
├── scripts/dev.sh         # starts frontend + backend together
├── docs/                  # ADR, vision, roadmap, contributing
└── local/                 # untracked: rust-toys specs, LEARNING.md
```

## Tech

| Layer | Legacy (Flet PWA) | New Stack |
|-------|-------------------|-----------|
| **UI** | Flet (Python → Flutter) | React + Vite |
| **API** | N/A (direct localStorage) | FastAPI (Python) |
| **Storage** | Browser localStorage | SQLite (WAL, triggers) |
| **Registry** | N/A | Rust crate (planned) |
| **Desktop** | N/A | Tauri v2 (planned) |
| **CI/CD** | GitHub Actions → Pages | TBD |

---

_Built with obsessive accountability in mind._
