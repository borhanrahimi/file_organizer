# File Organizer desktop app

A Tauri + React + TypeScript interface for the Python organizer in
`../backend`. See [ADR 001](../docs/decisions/001-frontend-framework.md) for
why Tauri, and [ADR 002](../docs/decisions/002-frontend-backend-communication.md)
and [architecture.md](../docs/architecture.md) for how it talks to the backend.

## Run

Install the backend first, from the repository root:

```bash
python3 -m pip install -e ./backend
```

Then, from `frontend/`:

```bash
npm install
npm run tauri dev
```

The app starts `python3 -m organizer.server` with a free port and a random
token, and stops it when the app quits. Set `ORGANIZER_PYTHON` to the Python
executable to use, for example a virtual environment's:

```bash
ORGANIZER_PYTHON=../.venv/bin/python npm run tauri dev
```

## Layout

- `src/App.tsx` — the status screen: state, Start/Stop, folders, categories,
  and recent activity. Polls the backend every 2 seconds while visible.
- `src/api.ts` — typed client for the backend's HTTP API.
- `src-tauri/src/lib.rs` — starts and stops the backend process and gives the
  window its port and token (`backend_connection` command).

## Checks

```bash
npm run build                  # TypeScript type-check and production build
(cd src-tauri && cargo test)   # backend start/stop tests; needs the backend installed
```
