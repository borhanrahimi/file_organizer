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
