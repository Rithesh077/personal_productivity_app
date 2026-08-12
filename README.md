# Stride

**Plan. Execute. Improve.**

A privacy-first personal system built for exactly one user. It answers one question: _"Does this reduce the friction in my day?"_

No cloud. No accounts. No integrations. All data stays on the device.

---

## Architecture

| Directory | Stack | Purpose |
|-----------|-------|---------|
| `frontend/` | React + Vite | UI |
| `backend/` | Python + FastAPI + SQLite | API + storage |
| `registry/` | Rust (planned) | Encrypted storage (keys + logbook) |

The legacy Flet PWA (`src/`) is archived. See [ADR-025](docs/ADR.md).

## Features

- **Hierarchical Goals** — Create goals with tasks and sub-tasks, cascading completion via SQLite triggers
- **Priority Task List** — A DMN-rescue queue for immediate, non-nested actions with tags
- **Analytics Dashboard** — Completion rate, on-time %, same-day execution, tag breakdown
- **Multi-step Goal Wizard** — Three-step creation: title → tasks/subtasks → review
- **Inline Editing** — Double-click-to-edit titles, inline add fields
- **Full REST API** — Every mutation returns the full updated Goal for clean state sync
- **Responsive** — Desktop top nav, mobile bottom tab bar

## Quick Start

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

### Migrating from the old PWA

```bash
# 1. Export localStorage from the browser console (see script header for details)
# 2. Save to data/export.json
python scripts/migrate_data.py data/export.json
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
├── scripts/
│   ├── dev.sh             # starts frontend + backend together
│   └── migrate_data.py    # localStorage → SQLite migration
├── docs/                  # ADR, vision, roadmap, contributing
├── local/                 # untracked: rust-toys specs, LEARNING.md
└── src/                   # ARCHIVED: Flet PWA
```

## Tech

| Layer | Stack |
|-------|-------|
| **UI** | React 19 + Vite |
| **API** | FastAPI (Python) |
| **Storage** | SQLite (WAL, cascading triggers) |
| **Registry** | Rust crate (planned: Argon2 + ChaCha20-Poly1305) |
| **Desktop** | Tauri v2 (planned) |

---

_Built with obsessive accountability in mind._
