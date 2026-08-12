# Stride

**Plan. Execute. Improve.**

A privacy-first personal system built for exactly one user. It answers one question: _"Does this reduce the friction in my day?"_

No cloud. No accounts. No integrations. All data stays on the device.

---

> ## Project structure
>
> As of **Aug 3, 2026**, Stride is a three-part system:
>
> | Directory | What | Status |
> |-----------|------|--------|
> | `frontend/` | React + Vite UI | Scaffolded |
> | `backend/` | Python + FastAPI API + SQLite | Scaffolded |
> | `registry/` | Rust encrypted storage (keys + logbook) | Scaffolded |
> | `src/` | **Legacy** Flet PWA (still deployed, still works) | Active until React has parity |
>
> The Flet PWA stays live on GitHub Pages until the new stack reaches feature parity ([ADR-027](docs/ADR.md)).
>
> Read [VISION.md](docs/VISION.md) for where this is going, and [ADR-025 onward](docs/ADR.md) for the restructure decisions.

---

## Features (current, via Flet PWA)

- **Hierarchical Goals** — Create goals with tasks and sub-tasks, cascading completion logic
- **Priority Tasks List** — A DMN-rescue queue for immediate, non-nested actions
- **Analytics Dashboard** — Completion rate, on-time %, same-day execution metrics
- **Inline Editing** — Tap-to-edit titles, inline add fields (Notion-style)
- **Schema Versioning** — Data survives app updates with migration support
- **Concurrency Safe** — `asyncio.Lock` serializes all storage operations
- **PWA** — Add to homescreen, works offline

## Quick Start

### Legacy Flet PWA

```bash
uv sync
uv run flet run --web      # web
uv run flet run             # desktop
uv run pytest tests/ -v    # 67 tests
```

### New stack (when built)

```bash
./scripts/dev.sh            # starts both frontend and backend
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
├── frontend/              # React + Vite (new UI)
├── backend/               # FastAPI + SQLite (new API)
├── registry/              # Rust crate (keys + logbook)
├── src/                   # LEGACY: Flet PWA (deployed, active)
├── tests/                 # LEGACY: pytest (67 tests)
├── scripts/dev.sh         # dev startup
├── docs/                  # ADR, vision, roadmap, contributing, learning
└── local/                 # untracked: JDs, rust-toys specs
```

## Tech

| Layer | Current (Flet PWA) | Next |
|-------|-------------------|------|
| **UI** | Flet (Python → Flutter) | React + Vite |
| **API** | N/A (direct localStorage) | FastAPI (Python) |
| **Storage** | Browser localStorage | SQLite |
| **Registry** | N/A | Rust crate (Argon2 + ChaCha20-Poly1305) |
| **Desktop** | N/A | Tauri v2 (planned) |
| **CI/CD** | GitHub Actions → Pages | TBD |

---

_Built with obsessive accountability in mind._
