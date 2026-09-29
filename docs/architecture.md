# Architecture

## Current status and structure

The Python backend runs from the terminal or a macOS LaunchAgent. The frontend
is planned; its framework and communication method have not been selected.

- `backend/src/organizer/` contains application startup, file operations,
  filesystem watching, and readiness tracking.
- `backend/test/` contains automated tests.
- `frontend/` is reserved for the desktop interface.
- `docs/` contains shared project documentation.

## Configuration and startup

`__main__.py` configures logging and reads `config.yaml` from the working
directory. Run from the repository root. The source folder, destination folder,
and categories come from configuration; there is no automatic Downloads default.
Local `config.yaml` is excluded from Git; `config.example.yaml` is the template.

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

- `get_category()` selects a category by extension, falling back to `Others`.
- `clean_filename()` adjusts capitalization, spaces, and parentheses.
- `unique_path()` chooses a numbered alternative if the destination exists.
- `organize_file()` creates the category folder, moves the file, and logs success.

Collision handling is a check followed by a move, not an atomic guarantee
against concurrent writers.

### Logging

Successful moves record source and destination paths. Pending-file operation
failures include exception details. Python logging uses standard error, so
successful move messages also appear in the LaunchAgent's error log.
See the [README](../README.md) for service and log commands.

## Planned frontend/backend boundary

The frontend will display status, collect settings, and request actions.
The backend will own file operations, validation, readiness, and watcher state.
The interface, process ownership, duplicate-instance protection, and behavior
when closing the UI still need design and implementation.

## Validation

Run from the repository root:

```bash
python3 -m pytest backend/test -v
```

At the readiness integration checkpoint, all 31 automated tests passed.
Coverage includes startup files, temporary downloads, created and moved files,
changing files, duplicate events, disappearing files, and retrying a failed move.

A manual background-service check wrote five lines over five seconds. The file
remained in source during writing, then appeared in `organized/Documents` with
all five lines intact. This verifies that scenario, not every download pattern.

## Remaining limitations

- Three seconds without observed changes cannot guarantee completion.
- Pending work is held in memory; a restart reconstructs it through the scan.
- Persistent move failures can be retried indefinitely; retry limits and backoff
  are not implemented.
- Configuration validation, duplicate-instance prevention, and comprehensive
  scan/event error recovery remain future work.
- Compound extensions such as `.tar.gz` and awkward title-casing remain unresolved.

See the [roadmap](../ROADMAP.md) for completed work and next steps.
