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
- [x] Separate file operations, folder watching, and application startup into modules
- [x] Test the organizer in the background and confirm move messages reach the log file
- [x] Verify autostart after logging out and back in
- [x] Finish and validate the macOS LaunchAgent configuration
- [x] Document how to start, stop, and disable the background organizer
- [x] Watch for newly created files inside subfolders
- [x] Ignore directory events and the exact .DS_Store filename

## Next
- [ ] Run the new directory-handler test
- [ ] Add permanent tests for .DS_Store, ordinary files, and similarly named files
- [ ] Scan files already present before startup
- [ ] Handle unfinished downloads before moving them
- [ ] Record a short demo GIF for the README

## Later / optional
- [ ] AI-based smart naming (reads file content, not just filename)
- [ ] Tray/menu-bar app instead of a background script
- [ ] Undo/history so a bad auto-move is reversible
- [ ] Build a macOS menu-bar interface with start/stop controls
- [ ] Package the organizer as a standalone macOS .app

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
- macOS autostart and background logging work and are documented.
- Watching subfolders was verified with a sample file.
- Directory and .DS_Store guards passed temporary checks.
- test/test_watcher.py now contains a directory-handler test.
- The permanent test suite has not been rerun since adding that test.

## Next session
- Run python3 -m pytest -v.
- Add the remaining three watcher tests.
- Confirm the background organizer was restarted to load the latest guard.