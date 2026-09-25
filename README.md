# File Organizer

A background tool that watches a folder (like Downloads) in real time and
automatically sorts new files into category subfolders, cleans up messy
filenames, and never overwrites anything.

<!-- Demo GIF goes here once recorded -->
<!-- ![demo](docs/demo.gif) -->

## What it does

- Watches a folder in real time (using `watchdog`) instead of polling
- Sorts files into category folders — Images, Documents, Videos, Music,
  Archives — fully configurable, not hardcoded
- Cleans up filenames (e.g. `final_report FINAL (2).docx` -> `Final_Report_Final_2.docx`)
- Never overwrites files — if a name is already taken, it adds a numbered
  suffix (`report_1.pdf`, `report_2.pdf`, ...) instead of destroying anything
- Configured entirely through a `config.yaml` file — no code editing needed
  to change which folder is watched or what counts as which category

## Why

Downloads folders are one of the messiest, most neglected parts of a
computer. This project applies a small, well-tested piece of automation to a
real everyday problem, rather than being a toy exercise.

## Install

```bash
pip install -e .
```

## Configuration

Copy the example config and edit it to match your setup:

```bash
cp config.example.yaml config.yaml
```

Then edit `config.yaml`:

```yaml
watch_folder: "/path/to/folder/to/watch"
destination_root: "/path/to/folder/where/organized/files/go"

categories:
  Images:
    - .jpg
    - .png
  Documents:
    - .pdf
    - .docx
  # add or edit categories freely — no code changes needed
```

`config.yaml` is your personal, local configuration and is not tracked by
git (see `.gitignore`) — only `config.example.yaml` is committed, as a
template.

## Usage

Run from the project root so the organizer can find `config.yaml`:

```bash
python3 -m organizer
```

It'll print `Watching folder: ...` and run until you stop it with `Ctrl+C`.

## Background operation on macOS

These commands manage the LaunchAgent named `com.borhan.file-organizer`.
They assume its configuration has already been saved to
`~/Library/LaunchAgents/com.borhan.file-organizer.plist`. This personal file
is outside the repository; installing the Python package does not create it.

The LaunchAgent must use your Python executable with the arguments
`-u`, `-m`, and `organizer`, set `WorkingDirectory` to your project root,
and set `RunAtLoad` to `true` to start at login. It reads the same
`config.yaml` as a manual run.

In the commands below, `$(id -u)` supplies your numeric user ID so
`launchctl` manages the job in your login session.

### Start and check status

Stop any terminal-run organizer with `Ctrl+C` first, so only one instance
watches the folder. If the background job is not already loaded, start it:

```bash
launchctl bootstrap "gui/$(id -u)" ~/Library/LaunchAgents/com.borhan.file-organizer.plist
```

Check its status:

```bash
launchctl print "gui/$(id -u)/com.borhan.file-organizer"
```

Look for `state = running`. If the job is not loaded, the status command
reports that it cannot find the service. If it is loaded but not running,
check the logs below.

### Stop the current job

```bash
launchctl bootout "gui/$(id -u)/com.borhan.file-organizer"
```

This stops and unloads the job. It can still start at your next login.
Running `bootout` on an already unloaded job reports an error.

### Disable or re-enable autostart

To prevent future startup, disable the job. If it is currently loaded,
also run `bootout` to stop it now:

```bash
launchctl disable "gui/$(id -u)/com.borhan.file-organizer"
launchctl bootout "gui/$(id -u)/com.borhan.file-organizer"
```

To re-enable autostart:

```bash
launchctl enable "gui/$(id -u)/com.borhan.file-organizer"
```

After enabling it, use the `bootstrap` command above to start it immediately
if it is not loaded, or let it start at your next login.

### Read the logs

With the configured log paths, read startup output and recent move messages
or errors using:

```bash
tail -n 20 ~/Library/Logs/file-organizer.log
tail -n 20 ~/Library/Logs/file-organizer-error.log
```

Python logging writes to standard error by default, so successful `INFO`
move messages also appear in `file-organizer-error.log`. Each move entry
records the timestamp, source path, and destination path. Log files appear
when the background job starts; if startup fails, check the error log.

## Architecture

Watched folder -> `watchdog` observer -> `organize_file()` -> destination
folders (deduplicated via `unique_path()`). See `docs/architecture.md` for
the full breakdown and design decisions.

- `core.py` handles categorization, filename cleanup, collision handling, and file moves.
- `watcher.py` handles filesystem events and the observer loop.
- `__main__.py` configures logging, reads `config.yaml`, and starts the watcher.

## Development

```bash
pip install -e .
pip install pytest pyyaml
pytest -v
```

## Roadmap

See `ROADMAP.md` for what's done and what's next.

## License

MIT
