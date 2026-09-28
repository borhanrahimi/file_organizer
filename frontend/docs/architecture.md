# Architecture

## Current status

File Organizer currently has a working Python backend.
The frontend has not been implemented.

The backend runs from the terminal or through a macOS LaunchAgent.
It reads config.yaml from the repository root.

## Repository structure

```text
file_organizer/
├── backend/
│   ├── pyproject.toml
│   ├── src/organizer/
│   │   ├── __init__.py
│   │   ├── __main__.py
│   │   ├── core.py
│   │   └── watcher.py
│   └── test/
│       ├── test_core.py
│       └── test_watcher.py
├── frontend/
│   └── README.md
├── docs/
│   └── architecture.md
├── .github/workflows/tests.yaml
├── config.example.yaml
├── config.yaml
├── README.md
└── ROADMAP.md
```

config.yaml contains local settings and is not tracked by Git.

## Current backend responsibilities

### Application startup: __main__.py

- Configure logging.
- Read config.yaml.
- Pass the source folder, destination folder, and categories to the watcher.

Configuration currently depends on the working directory.
Run the application from the repository root.

### File operations: core.py

- Select a category based on the file extension.
- Clean the filename.
- Choose a numbered alternative when the destination already exists.
- Move the file into its category folder.
- Log successful moves.

Unknown extensions are placed in Others.

### Filesystem handling: watcher.py

- Scan existing files at startup, including subfolders.
- Watch recursively for newly created and moved files.
- Use the destination path when processing move events.
- Ignore directory events and the exact filename .DS_Store.
- Skip .crdownload, .part, and .download extensions.
- Exclude the destination folder from the startup scan.

The startup scan completes before live watching begins.

## Current processing flow

```text
Start application
    |
Read configuration
    |
Scan existing files
    |
Start filesystem observer
    |
Receive created or moved event
    |
Apply file checks
    |
Choose category and clean filename
    |
Choose available destination name
    |
Move file and log success
```

The startup scan and event handlers both call organize_file().

When a temporary download is renamed to its final filename,
a move event can allow it to be organized.

## Planned frontend

The first frontend is intended to be a local macOS interface.

Its responsibilities will include:

- Displaying running, stopped, and error states.
- Providing start and stop controls.
- Letting the user select source and destination folders.
- Displaying recent operations and understandable errors.
- Explaining that starting the organizer also processes existing files.

The frontend framework has not been selected.

The frontend will request backend actions rather than move files itself.

## Planned frontend/backend boundary

The backend will remain responsible for:

- Validating configuration and paths.
- Deciding whether a file is ready to move.
- Performing file operations.
- Managing watcher lifecycle.
- Reporting status and operation results.

The frontend will remain responsible for:

- Presenting information.
- Collecting user choices.
- Sending supported requests.
- Displaying results and errors.

The communication method is undecided.

Before implementation, document:

- Supported requests and responses.
- Error formats.
- How status updates reach the frontend.
- Which process owns the watcher.
- Whether closing the frontend leaves the organizer running.
- How the existing LaunchAgent fits into the desktop application.
- How duplicate organizer instances are prevented.

## Safety requirements: planned work

These requirements are not all implemented yet:

- Validate source and destination folders and reject unsafe overlap.
- Prevent category paths from escaping the destination.
- Handle files still being written, including retries.
- Recover from permission errors and disappearing files.
- Prevent duplicate watcher instances.
- Define collision behavior under concurrent file operations.
- Limit file access to the locations needed by the application.
- Avoid executing shell commands constructed from user input.

The backend must enforce these rules even when requests come
from the frontend.

## Current limitations

- Temporary extensions are skipped, but files written directly to
  their final filename can still be moved before writing finishes.
- Files arriving between the startup scan and observer startup
  may be missed.
- Live event handlers do not have the startup scan's destination
  exclusion, so placing the destination inside the source is unsafe.
- File-operation errors do not yet have a recovery or retry strategy.
- Collision handling checks whether a name exists before moving;
  it is not an atomic guarantee against concurrent writers.
- Only the final extension is checked, so .tar.gz needs special handling.
- Filename title-casing can produce awkward capitalization.

## Testing and operation

Run from the repository root:

```bash
python3 -m pip install -e ./backend
python3 -m pytest backend/test -v
```

Tests cover core file operations and watcher behavior.
Passing tests do not establish that every safety requirement is complete.

See README.md at the repository root for background-service commands.
See ROADMAP.md for completed work and upcoming tasks.