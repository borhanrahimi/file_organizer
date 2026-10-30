# Architecture

## Current status and structure

The organizer runs in two ways:

- **Desktop app (server mode).** The Tauri app in `frontend/` starts the
  Python backend as a child process. The backend runs a local HTTP API and
  owns the watcher thread. See
  [ADR 002](decisions/002-frontend-backend-communication.md).
- **Terminal mode.** `python3 -m organizer` (also used by the macOS
  LaunchAgent) reads `config.yaml` and watches until stopped.

Both modes take the same lock file, so they never watch at the same time.

- `backend/src/organizer/` contains application startup, the HTTP API, the
  watcher service, file operations, filesystem watching, and readiness tracking.
- `backend/test/` contains automated tests.
- `frontend/` contains the Tauri + React desktop app.
- `docs/` contains shared project documentation.

## Configuration and startup

`__main__.py` configures logging and loads `config.yaml` from the working
directory through `load_config()` in `config.py`. Run from the repository root. The source folder, destination folder,
and categories come from configuration; there is no automatic Downloads default.
Local `config.yaml` is excluded from Git; `config.example.yaml` is the template.

`config.py` splits loading into `read_config_file()` (parse YAML only) and
`validate_config()` (check the values). `load_config()` does both.
`save_config()` writes a temporary file and then replaces the real one, so a
crash never leaves a half-written settings file.

`validate_config()` raises `ConfigError` for a missing or invalid file, missing
settings, empty folder paths, a watch folder that does not exist, a watch folder
that is the same as or inside the destination, category names that are not
plain folder names (such as `../x` or `a/b`), and extensions that do not start
with a dot. `__main__.py` prints the message and exits with status 1.

In terminal mode, `__main__.py` then takes the organizer lock (see
[lock.py](#duplicate-instances-lockpy)). If another organizer holds it, it
prints the message and exits with status 1.

## Processing flow

```text
Start observer
    |
Scan existing files + receive created/moved events
    |
Filter eligible paths and add to incoming queue
    |
Transfer paths to pending set (combine duplicates)
    |
Repeated readiness checks
    |
Categorize, clean filename, choose available destination
    |
Move file and log success
```

## Components

### Filesystem handling: watcher.py

- Start observing before scanning existing files, including subfolders.
- Queue startup files and files reported by created or moved events.
- Use the new destination path for moved-file events.
- Skip directory events, the exact `.DS_Store` filename, temporary download
  extensions (`.crdownload`, `.part`, `.download`), and destination paths.
- Pass incoming paths through a thread-safe queue from event handling to the
  processing loop. The loop owns the pending set and readiness tracker.
- Combine duplicate pending paths and check pending work once per second.
- Remove missing files and clear their readiness observations.
- Catch file-operation `OSError` failures, log them, and keep the file pending
  for another attempt after a fresh stability check.
- Stop and join the observer when the processing loop exits.

The observer detects events while the loop checks known pending files.
Files are not moved immediately upon receiving an event. Directory move events
are ignored; scanning the contents of a moved directory is not implemented.

- Record each successful move and each failed attempt in the activity log,
  when one is given.

### File readiness: readiness.py

`get_file_signature()` reads device, inode, size, and modification time.
`FileReadinessTracker` records each signature with a monotonic timestamp.
A detected change restarts the default three-second stability period.

Readiness is checked repeatedly without sleeping inside event handlers.
After a successful move, the tracker forgets the path. Tests inject a clock
so elapsed-time behavior can be checked without real delays.

An unchanged signature is a readiness signal, not proof that writing has
finished. A paused download can resume later, and a file can change between
the final check and the move.

### File operations: core.py

- `get_category()` selects the category whose extension the filename ends with,
  preferring the longest match (`.tar.gz` over `.gz`) and falling back to `Others`.
- `clean_filename()` adjusts capitalization, spaces, and parentheses.
- `unique_path()` chooses a numbered alternative if the destination exists.
- `organize_file()` creates the category folder, moves the file, logs success,
  and returns the destination path.

Collision handling is a check followed by a move, not an atomic guarantee
against concurrent writers.

### Logging

Successful moves record source and destination paths. Pending-file operation
failures include exception details. Python logging uses standard error, so
successful move messages also appear in the LaunchAgent's error log.
See the [README](../README.md) for service and log commands.

## Server mode

### Server entry point: server.py

`python3 -m organizer.server --port <port>` runs the API with Uvicorn on
`127.0.0.1` only, never on the local network.

| Option | Meaning |
|---|---|
| `--port` | Required. The app picks a free port for each launch. |
| `--settings` | Settings file to read and save. The app passes a file in its own app data folder. Default: `settings.yaml` in the organizer's data folder. |
| `--lock-file` | Lock file. Default: `organizer.lock` in the organizer's data folder (see below). Tests pass their own. |
| `--parent-pid` | The app's process id. The server shuts down when that process is gone. |

The token comes from the `ORGANIZER_TOKEN` environment variable, not from a
command-line option, because other users on the computer can read process
arguments. Without it the server prints `ORGANIZER_TOKEN must be set.` and
exits with status 1.

`POST /shutdown` stops the watcher, then tells Uvicorn to exit after the
response is sent. When Uvicorn exits for any reason (shutdown request,
`Ctrl+C`, or the parent process disappearing), the server stops the watcher
before the process ends.

`--parent-pid` covers the app crashing or being force-quit before it can send
`/shutdown`. A background thread checks once per second whether the server's
parent is still that process; the operating system gives orphaned processes a
new parent. This relies on Unix behavior; on Windows the app still ends the
backend on a normal quit.

### HTTP API: api.py

`create_app(token, service, on_shutdown)` builds the FastAPI app.

- A middleware compares the `Authorization: Bearer <token>` header in
  constant time (`secrets.compare_digest`) and answers `401` otherwise.
- CORS middleware runs before the token check. Browsers send a preflight
  `OPTIONS` request without the token before any request that carries one.
  Only the app window's origins are allowed: `http://localhost:1420`
  (development), `tauri://localhost` (macOS/Linux) and `http://tauri.localhost`
  (Windows). Preflights from other websites are refused.

| Request | Response |
|---|---|
| `GET /status` | `{"state": "running" \| "stopped" \| "error", "message": ...}` |
| `POST /start` | The new status. Starting while running changes nothing. |
| `POST /stop` | The new status. Stopping while stopped changes nothing. |
| `GET /settings` | `watch_folder`, `destination_root` (both `null` before the first save) and `categories` |
| `PUT /settings` | Body `{"watch_folder": ..., "destination_root": ...}`. Validates, saves, and returns the settings. Categories are kept. |
| `GET /activity` | Up to 100 recent events, newest first |
| `POST /shutdown` | `{"state": "stopped", "message": null}`, then the process exits |

### Watcher ownership: service.py

`OrganizerService` owns the settings, the watcher thread, the lock, and the
activity log.

- `start()` validates the saved settings with `validate_config()`, takes the
  lock, and runs `start_watching()` on a daemon thread with a fresh
  `threading.Event`.
- `stop()` sets the event and waits for the thread to finish, so an
  in-progress move completes. It then releases the lock.
- `update_settings()` refuses to run while the watcher thread is alive.
- If the watcher thread raises (for example, the source folder was deleted),
  the state becomes `error` with the message
  `The organizer stopped unexpectedly: <reason>`. `start()` and `stop()` clean
  up the dead thread and clear the error; saving valid settings also clears it.
- A settings file that exists but cannot be read sets `error` at startup, with
  the `ConfigError` message. A missing settings file is normal on first run.

Start, stop, and settings changes are serialized by one lock, so two requests
cannot start two watcher threads. A second, smaller lock protects the state
that the watcher thread changes when it crashes.

### Activity: activity.py

`ActivityLog` keeps the most recent 100 events in a `deque` protected by a
`threading.Lock`, because the watcher thread writes and request handlers read.
Each event has an ISO 8601 UTC `timestamp`, a `type` (`moved` or `error`), the
`source` path, and either `destination` or `message`. Events are lost when the
backend exits; the log files keep the full history.

### Duplicate instances: lock.py

`OrganizerLock` takes an exclusive, non-blocking operating-system lock
(`fcntl.flock` on macOS/Linux, `msvcrt.locking` on Windows). The operating
system releases it if the process dies, so a crash never leaves a stale lock.

The default lock file is shared by terminal mode, the LaunchAgent, and the app:

| Platform | Data folder |
|---|---|
| macOS | `~/Library/Application Support/File Organizer/` |
| Windows | `%APPDATA%\File Organizer\` |
| Linux | `$XDG_STATE_HOME/file-organizer/` (default `~/.local/state/file-organizer/`) |

The lock is held only while the watcher runs, not while the server is merely
open. A held lock makes `POST /start` return `409 already_running`.

## Desktop app: frontend/

The Tauri app (`frontend/src-tauri/src/lib.rs`) owns the backend process:

1. At launch it picks a free port, generates a random token (UUID v4), and
   runs `python3 -m organizer.server` with `--port`, `--settings` (in the app
   data folder), `--parent-pid`, and `ORGANIZER_TOKEN`. Set `ORGANIZER_PYTHON`
   to use a different Python executable.
2. The window calls the `backend_connection` command to get the port and
   token. The command reports an error if Python could not be started or the
   backend has already exited.
3. On quit (`RunEvent::Exit`) it sends `POST /shutdown`, waits up to five
   seconds, then kills the process if it is still running.

The React interface (`frontend/src/`) polls `GET /status` and `GET /activity`
every two seconds while the window is visible. It shows the state, start and
stop buttons, folder pickers, the categories, and recent activity. Closing the
window quits the app and stops the organizer (Stage 1 in ADR 002); the window
says so next to the Start button.

## Error behavior

Errors use an HTTP status code and the body
`{"error": {"code": "...", "message": "..."}}`. `code` is for programs;
`message` is shown to the user as-is.

| Status | Code | When |
|---|---|---|
| 400 | `invalid_settings` | `PUT /settings` or `POST /start` with invalid or missing folders. The message is the `ConfigError` text. |
| 400 | `invalid_request` | The request body is missing fields or is not JSON. |
| 401 | `unauthorized` | Missing or wrong token. |
| 409 | `already_running` | `POST /start` while another organizer holds the lock. |
| 409 | `organizer_running` | `PUT /settings` while the watcher runs. |
| 500 | `internal_error` | Anything unexpected; details go to the log. |

Failures inside the watcher are not request errors:

- A failed move is logged with its traceback, recorded as an `error` activity
  event, and retried after a fresh stability period. The file stays in the
  source folder.
- A crash of the watcher thread sets the status to `error` with a message.

## File-safety requirements

These rules hold in both modes, and the backend enforces them even when
requests come from the app:

| Requirement | How |
|---|---|
| Validate folders before starting | `validate_config()` on every `PUT /settings` and every start |
| No unsafe overlap | The watch folder may not be the destination or inside it; files already inside the destination are never queued |
| Category folders stay in the destination | Category names must be plain folder names |
| Never overwrite | `unique_path()` adds `_1`, `_2`, ... when a name is taken |
| Wait for files being written | Readiness checks; temporary download extensions are skipped |
| Survive permission errors and disappearing files | `OSError` is caught, recorded, and retried; missing files leave the queue |
| One organizer at a time | Operating-system lock shared by every mode |
| Stop safely | Stopping waits for an in-progress move to finish |
| Local only | The API listens on `127.0.0.1`, requires a per-launch token, and allows only the app's origins |
| No shell commands from user input | Paths are only used with `pathlib`, `shutil`, and `os`; the app starts Python with an argument list, not a shell string |
| Settings saved safely | Written to a temporary file, then renamed over the old one |

Not guaranteed:

- Collision handling is a check followed by a move, not atomic against another
  program writing the same name at the same moment.
- Three unchanged seconds do not prove a download has finished.
- Moves are not reversible from the app; the activity list and logs show
  where each file went.

## Validation

Run from the repository root:

```bash
python3 -m pytest backend/test -v
```

All 87 Python tests pass. Coverage includes startup files, temporary
downloads, created and moved files, changing files, duplicate events,
disappearing files, retrying a failed move, configuration errors, multi-part
extensions, the activity log, the lock file, the watcher service (start, stop,
crash, settings while running), every API endpoint and error, CORS, and the
server process exiting on `/shutdown` and when its parent exits.

The Tauri side has two Rust tests (`cargo test` in `frontend/src-tauri`, with
the Python package installed): quitting sends `/shutdown` and the backend
exits, and a backend that does not answer is killed.

A manual background-service check wrote five lines over five seconds. The file
remained in source during writing, then appeared in `organized/Documents` with
all five lines intact. This verifies that scenario, not every download pattern.

## Remaining limitations

- Three seconds without observed changes cannot guarantee completion.
- Pending work is held in memory; a restart reconstructs it through the scan.
- Persistent move failures can be retried indefinitely; retry limits and backoff
  are not implemented.
- A file that keeps failing to move adds an `error` activity event on every
  retry, which can push older events out of the 100-event list.
- The app needs Python and the backend package installed; packaging the
  backend as a standalone sidecar is future work.
- `clean_filename()` treats only the last extension as the extension, so
  `backup.tar.gz` becomes `Backup.Tar.gz`; title-casing can also be awkward.

See the [roadmap](../ROADMAP.md) for completed work and next steps.
