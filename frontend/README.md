# Frontend

React + Vite. The UI layer for Stride.

Consumes the Python backend API over HTTP (`/api/*`). In dev mode, Vite proxies API calls to `localhost:8000`.

## Setup

```bash
cd frontend
npm install
npm run dev
```

## Structure

```
src/
├── components/
│   ├── GoalCard.jsx       # hierarchical goal display with inline editing
│   ├── GoalWizard.jsx     # multi-step goal creation/edit flow
│   ├── TaskListCard.jsx   # priority queue item card
│   └── StatCard.jsx       # reusable metric display card
├── pages/
│   ├── Planner.jsx        # goals page (list, CRUD, wizard)
│   ├── TaskList.jsx       # priority task list page
│   └── Analytics.jsx      # performance metrics page
├── hooks/
│   └── useApi.js          # generic fetch + mutation hooks
├── services/
│   └── api.js             # endpoint definitions
├── styles/
│   └── tokens.css         # design tokens (colors, spacing, typography)
├── App.jsx                # routing + navigation
└── main.jsx               # React entry point
```

## Design System

All design tokens are in `tokens.css` as CSS custom properties:
- **Colors**: teal, amber, red, purple, green accents on a dark bg (`#0B0F1A`)
- **Typography**: Inter font family, 11-28px scale
- **Spacing**: 4-40px scale
- **Components**: per-component CSS files colocated with their `.jsx`

## Architecture

- **Components are pure** — they receive data and callbacks via props. No direct API calls.
- **Pages are orchestrators** — they fetch data via `useApi`, handle mutations, and wire components together.
- **`api.js` is the single source** for all endpoint definitions. Components and pages never construct URLs.
