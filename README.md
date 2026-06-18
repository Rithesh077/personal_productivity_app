# Stride

**Plan. Execute. Improve.**

A privacy-first PWA that answers one question: _"Did I actually do what I planned?"_

No AI. No integrations. No account. Runs entirely in your browser using localStorage.

---

## Features

- **Hierarchical Goals** — Create goals with tasks and sub-tasks, cascading completion logic
- **Priority Tasks List** — A DMN-rescue queue for immediate, non-nested actions
- **Analytics Dashboard** — Completion rate, on-time %, same-day execution metrics
- **Inline Editing** — Tap-to-edit titles, inline add fields (Notion-style)
- **Schema Versioning** — Data survives app updates with migration support
- **Concurrency Safe** — `asyncio.Lock` serializes all storage operations
- **PWA** — Add to homescreen, works offline

## Tech

- **[Flet](https://flet.dev)** — Python → Web / Desktop / Mobile via Flutter
- **Client Storage** — Zero backend, all data in browser `localStorage`
- **CI/CD** — Auto-deploy to GitHub Pages on push to `main`

## Quick Start

```bash
# install dependencies
uv sync

# run locally (web)
uv run flet run --web

# run locally (desktop)
uv run flet run

# run tests
uv run pytest tests/ -v
```

## Documentation

| Document | Description |
|----------|-------------|
| [Contributing](docs/CONTRIBUTING.md) | Project structure, setup, testing, deployment |
| [Architecture Decision Records](docs/ADR.md) | Every architectural decision from Flask → Flet |
| [Roadmap](docs/ROADMAP.md) | Feature roadmap and to-dos |

## Project Structure

```
src/
├── main.py              # entry point, navigation, routing
├── models/              # Goal, Task, SubTask, TaskItem
├── views/               # planner, task list, analytics
├── components/          # goal card, wizard, task list card
├── services/storage.py  # SharedPreferences CRUD + schema versioning
├── constants/design.py  # design tokens
└── utils/               # time, color, math helpers
tests/                   # 67 unit tests (pytest)
docs/                    # ADR, contributing, roadmap
```

---

_Built with obsessive accountability in mind._
