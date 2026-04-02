# Stride

**Plan. Execute. Improve.**

A PWA that answers one question: *"Did I actually do what I planned today?"*

## What it does

1. **Evening** — Plan tomorrow's tasks
2. **Next day** — Work through the list, check off what you actually did
3. **Review** — See your follow-through rate and 7-day trends
4. **Repeat** — Plan better, informed by your own data

No AI. No integrations. No account. Runs entirely in your browser using localStorage.

## Tech

- **[Flet](https://flet.dev)** — Python → Web/Desktop/Mobile
- **Client storage** — Zero backend, all data stays in your browser
- **PWA** — Add to homescreen for quick access

## Run locally

```bash
uv run flet run --web
```

## Build for deployment

```bash
uv run flet build web -v
```

Deploy the `build/web` folder to GitHub Pages, Cloudflare Pages, or any static host.

## Project structure

```
src/
├── main.py              # App shell, theme, navigation
├── views/
│   ├── planner.py       # Daily planner (Today/Tomorrow)
│   └── analytics.py     # 7-day analytics dashboard
├── components/
│   ├── task_card.py      # Task card with checkbox
│   └── stat_card.py      # Metric display card
└── services/
    └── storage.py        # Client storage abstraction
```

## License

MIT
