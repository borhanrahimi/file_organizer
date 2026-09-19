# Architecture

## Overview

The organizer is a small pipeline: a watched folder feeds a file event to a
handler, which decides where the file belongs and what to call it, then moves
it and logs the result.

```
Downloads folder (watched)
        |
        v
watchdog observer  --  detects new file events in real time
        |
        v
organize_file()  --  categorizes and renames the file
        |              |
        v              v
destination folders   log file
(sorted by type)       (records every action)

        |
        v (optional, future)
AI naming  --  reads file content instead of just cleaning the existing name
```

## Components

**Downloads folder** — the source. No special setup; it's whatever folder
you point the tool at (defaults to `~/Downloads`).

**watchdog observer** — a Python library that subscribes to filesystem
events instead of polling the folder on a timer. This means new files are
picked up immediately, and the tool isn't wasting CPU checking a folder that
hasn't changed.

**`organize_file()`** — the core logic. It calls two smaller functions:
- `get_category(filename)` — looks up the file's extension in a dictionary
  and returns a category name (e.g. `"Images"`). Falls back to `"Others"`
  for unrecognized extensions, so nothing is silently skipped.
- `clean_filename(filename)` — lowercases the name, title-cases it, replaces
  spaces with underscores, and strips parentheses, while leaving the
  extension untouched.

**Destination folders** — created automatically as needed, one per category.

**Log file** — every move is recorded, so there's always a record of what
happened and when, useful for catching mistakes.

## Why these choices

- **watchdog over polling**: event-driven means instant reaction and no
  wasted CPU checking an unchanged folder.
- **Rule-based categorization before AI**: a dictionary lookup is fast, free,
  fully predictable, and good enough for the vast majority of files. AI-based
  naming is a real upgrade path, but it adds cost, latency, and complexity
  that isn't worth it until the basic version is solid and battle-tested.
- **"Others" fallback instead of skipping or erroring**: since this tool runs
  unattended in the background, a single unrecognized file type shouldn't
  stop everything else from being organized, and it shouldn't silently
  vanish either — it should end up somewhere visible.

## Known limitations

See `ROADMAP.md` for the current list of known rough edges and what's
planned next.
