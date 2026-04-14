# Stride

**Plan. Execute. Improve.**

A privacy-first PWA that answers one question: _"Did I actually do what I planned?"_

## What it does

1. **Plan** -- Set goals with tasks and sub-tasks
2. **Execute** -- Work through the list, check off what you did
3. **Review** -- See follow-through rate, on-time %, and same-day execution
4. **Repeat** -- Plan better, informed by your own data

No AI. No integrations. No account. Runs entirely in your browser using localStorage.

## Tech

- **[Flet](https://flet.dev)** -- Python to Web/Desktop/Mobile
- **Client storage** -- Zero backend, all data stays in your browser
- **PWA** -- Add to homescreen, works offline
- **Schema versioning** -- Data survives app updates

## Run locally

```bash
uv run flet run --web
```

## Build for deployment

```bash
uv run flet build web
```

## Features

- Create goals with tasks and sub-tasks
- Set custom or default (24h) deadlines
- Inline tap-to-edit titles (Notion-style)
- Inline add fields for rapid task/sub-task entry
- Mark complete with cascading completion logic
- Undo delete operations
- Reorder tasks and sub-tasks
- Completion percentage tracking
- Analytics dashboard:
  - Completion by level (goal/task/subtask)
  - Status distribution
  - On-time and same-day execution analysis
  - Recent goals progress
  - Completion history with badges
