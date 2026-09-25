# Roadmap

## Done
- [x] Project structure set up (src/organizer, tests, git, GitHub)
- [x] `get_category()` — sorts by extension, with "Others" fallback for unknown types
- [x] `clean_filename()` — lowercases, title-cases, strips spaces and parentheses
- [x] `organize_file()` — ties `get_category()` and `clean_filename()` together and actually moves files
- [x] Wire in `watchdog` for real-time folder watching
- [x] Test on a throwaway folder before pointing it at a real Downloads folder
- [x] Write automated tests (pytest) for `get_category` and `clean_filename`
- [x] Turn hardcoded CATEGORIES / watch folder into a config file or CLI args
- [x] Set up GitHub Actions CI to run tests automatically
- [x] Package it (pyproject.toml) so it's pip-installable
- [x] Log successful file moves with timestamps, source paths, and destination paths

## Next
- [ ] Record a short demo GIF for the README
- [ ] Separate file operations, folder watching, and application startup into modules
- [ ] Autostart on login (launchd on Mac / Task Scheduler on Windows)
- [ ] Finish and validate the macOS LaunchAgent configuration
- [ ] Test the organizer in the background and confirm move messages reach the log file
- [ ] Verify autostart after logging out and back in
- [ ] Document how to start, stop, and disable the background organizer

## Later / optional
- [ ] AI-based smart naming (reads file content, not just filename)
- [ ] Tray/menu-bar app instead of a background script
- [ ] Undo/history so a bad auto-move is reversible

## Known limitations
- `Path(filename).suffix` only grabs the last extension, so `backup.tar.gz` becomes
  `.gz`, not `.tar.gz`, and won't match the Archives category correctly. Needs a
  special case for multi-part extensions.
- `.title()` capitalizes small words oddly in some cases (e.g. `_At_`, `_Pm_` in
  timestamps, `Don'T` for words with apostrophes). Cosmetic, not fixed yet.

## Decisions made along the way
- Unknown file extensions fall back to an "Others" category rather than being
  skipped or raising an error — the goal is that every file always ends up
  somewhere, since this runs unattended in the background.
- Filenames are cleaned but not made "perfect" — good enough to be readable
  and sortable, not chasing 100% correctness on every edge case in v1.

- Learned the hard way that `assert some_function(...)` with no comparison
  is a near-useless test — it passes as long as the function returns
  anything truthy. Every real test compares against a specific, verified
  expected value.

- Successful moves are logged after shutil.move() completes, recording the
  timestamp, original path, and destination path.
- Logging currently writes to standard error. When run through the
  LaunchAgent, those messages are captured in its configured error log.


## Where I left off
- File-move logging works in the terminal.
- CI and packaging are complete.
- macOS autostart still needs verification.

## Next session
- Start the refactor by moving DownloadHandler into watcher.py.
- Update imports and run the tests.