# Contributing to Stride

> Stride is a personal productivity tracker. This document explains the project structure and development workflow for anyone reviewing the codebase (or future me).

## Prerequisites

- **Python 3.11+**
- **[uv](https://docs.astral.sh/uv/)** — fast Python package manager

## Setup

```bash
# clone and install
git clone https://github.com/Rithesh077/Stride.git
cd Stride
uv sync

# run locally (web)
uv run flet run --web

# run locally (desktop)
uv run flet run
```

## Project Structure

```
src/
├── main.py                  # entry point, navigation bar, routing
├── models/                  # data classes (Goal, Task, SubTask, TaskItem)
├── views/                   # page-level UI builders
│   ├── planner.py           # goal tracker (tab 1)
│   ├── task_list.py         # priority tasks list (tab 2)
│   └── task_list_analytics.py  # analytics for task list (tab 3)
├── components/              # reusable UI components
│   ├── goal_card.py         # hierarchical goal card
│   ├── goal_wizard.py       # multi-step goal creation
│   ├── task_list_card.py    # task list item card
│   ├── stat_card.py         # analytics stat card
│   └── analytics_charts.py  # chart components
├── services/
│   └── storage.py           # SharedPreferences CRUD + schema versioning
├── constants/
│   └── design.py            # design tokens (colors, sizes)
└── utils/
    ├── time_utils.py        # UTC, deadline, relative time functions
    ├── color_utils.py       # performance color mappings
    └── math_utils.py        # safe_percentage
```

## Testing

```bash
# run all tests
uv run pytest tests/ -v

# run a specific test file
uv run pytest tests/test_goal.py -v
```

Tests cover:
- **Models** — serialization roundtrips, completion logic, backwards compatibility
- **Utilities** — time calculations, math helpers, color mappings

## Architecture Decisions

See [ADR.md](./ADR.md) for a complete record of every architectural decision, from the Flask prototype to the current Flet PWA.

## Key Design Principles

1. **Privacy-first** — Zero backend, all data in browser localStorage
2. **Personal-first** — Built for one user (the author), not hypothetical users
3. **Accountability-focused** — Core question: "Did I do what I planned?"

## Deployment

Deploys automatically to GitHub Pages on push to `main` via the [deploy workflow](.github/workflows/deploy.yml).

```bash
# manual build (for testing)
flet publish src/main.py --base-url /Stride/
```

## Storage

Data is stored in browser `localStorage` via Flet's `SharedPreferences`:

| Key | Contents |
|-----|----------|
| `stride.goals` | All goals as JSON array |
| `stride.schema_version` | Current schema version (for migrations) |
| `stride.task_list` | Active priority task list items |
| `stride.task_list_completed` | Completed task list items |
| `stride.custom_tags` | User-created custom tags |

## Schema Versioning

When changing data models:
- **Additive changes** (new fields): Just add a default in `from_dict()`. No migration needed.
- **Breaking changes** (renames, type changes): Add a migration block in `storage.py::_run_migrations()` and bump `SCHEMA_VERSION`.
