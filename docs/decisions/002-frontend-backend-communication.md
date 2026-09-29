# 002: Frontend/backend communication and process ownership

## Status

Accepted (2026-09-29)

## Context

[ADR 001](001-frontend-framework.md) chose a Tauri + React frontend. The
Python backend currently runs on its own, from the terminal or a macOS-only
LaunchAgent, and has no way to receive requests or report status.

The frontend must show the organizer's real state, start and stop it, change
the source and destination folders, and show recent moves and errors. The
design must work on macOS, Windows, and Linux, and the backend must stay
responsible for validation and every file operation.

The organizer is a background tool: users expect it to keep sorting files when
its window is closed.

## Options considered

- **Local HTTP API (chosen).** The backend runs a small FastAPI server on
  `127.0.0.1`; React sends HTTP requests. Easy to test with a browser, `curl`,
  or pytest. Web APIs are a widely used skill. Needs protection against other
  local programs calling it.
- **Standard input/output messages.** Tauri writes JSON lines to the Python
  process and reads replies. Nothing is exposed on the network, but it needs
  custom message matching and is harder to test by hand.
- **Frontend reads config and log files directly.** No server needed, but
  status would be guessed from files rather than reported by the backend, and
  start/stop would not be possible.

## Decision

### Process ownership

The Tauri app owns the Python backend process. The backend process owns the
watcher.

1. When the Tauri app starts, it starts the backend as a child process
   ("sidecar").
2. The backend runs the HTTP server on its main thread and the watcher on a
   background thread.
3. **Start** and **Stop** requests start and stop the watcher thread. They do
   not start or stop the backend process.
4. When the Tauri app quits, it asks the backend to shut down, waits briefly,
   then ends the process if it has not exited. No backend process may be left
   running after the app quits.

### Transport and security

- The backend listens on `127.0.0.1` only, never on the local network.
- Tauri chooses a free port and a random secret token for each launch and
  passes both to the backend when starting it.
- Every request must include the token in an `Authorization: Bearer <token>`
  header. Requests without it get `401`. This stops web pages and other local
  programs from controlling the organizer.

### Requests and responses (first version)

All bodies are JSON.

| Request | Purpose | Success response |
|---|---|---|
| `GET /status` | Current state | `{"state": "running" \| "stopped" \| "error", "message": ...}` |
| `POST /start` | Start the watcher | `200` with the new status |
| `POST /stop` | Stop the watcher | `200` with the new status |
| `GET /settings` | Source, destination, categories | The settings |
| `PUT /settings` | Change source and destination | The saved settings |
| `GET /activity` | Recent moves and errors, newest first | A list of events |
| `POST /shutdown` | Stop the watcher and exit (used by Tauri on quit) | `200` |

Starting while running, or stopping while stopped, succeeds and changes
nothing. Settings cannot be changed while the watcher is running (`409`).

Activity is kept in memory, limited to the most recent 100 events. Each event
has a timestamp, a type (`moved` or `error`), the source path, and either the
destination path or an error message.

### Error format

Errors use an HTTP status code and this body:

```json
{"error": {"code": "invalid_settings", "message": "watch_folder is not an existing folder: /foo"}}
```

- `code` is stable and meant for the program (for example
  `invalid_settings`, `already_running`, `unauthorized`).
- `message` is meant for the user and reuses the existing `ConfigError`
  messages.
- `400` for invalid input, `401` for a missing or wrong token, `409` for a
  request that conflicts with the current state, `500` for unexpected errors.

### Status updates

The frontend asks for `GET /status` and `GET /activity` every 2 seconds while
the window is visible. Polling is simple and easy to debug; push updates
(Server-Sent Events or WebSockets) can replace it later if needed.

### Closing the window

Built in stages:

1. **Stage 1:** closing the window quits the app and stops the backend. The
   window states this before the user starts the organizer.
2. **Stage 2:** closing the window hides it. A tray/menu-bar icon offers
   Open, Pause/Resume, and Quit. Only Quit stops the backend.
3. **Stage 3:** optional start at login through Tauri's autostart plugin.

### The existing LaunchAgent

`python3 -m organizer` and the LaunchAgent remain available for development
and for macOS users until Stage 3 is complete, then the LaunchAgent is retired.
They must not run at the same time as the app (see below).

### Preventing duplicate instances

- Tauri's single-instance plugin stops a second copy of the app from opening;
  it focuses the existing window instead.
- The backend takes an exclusive lock file in the user's application data
  folder when the watcher starts. If the lock is already held (for example by
  the LaunchAgent), `POST /start` returns `409` with a message explaining that
  another organizer is running.

## Consequences

- The backend gains FastAPI and Uvicorn as dependencies and a new entry point
  for server mode. The existing terminal mode keeps working.
- The watcher loop must be stoppable from another thread; it currently runs
  until `Ctrl+C`.
- Activity must be recorded where moves and errors happen, not only logged.
- Settings can no longer rely on `config.yaml` in the working directory. A
  packaged app needs a per-user settings file in the operating system's
  application data folder; its path is passed from Tauri to the backend.
- The API is testable without the UI using FastAPI's test client and pytest.
- For distribution, the backend must be packaged as a standalone executable
  for each platform (for example with PyInstaller) and registered as a Tauri
  sidecar. During development, Tauri may run it with the local Python.
- Polling every 2 seconds adds a small, constant amount of work while the
  window is open.
