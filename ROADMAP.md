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
- [x] Scan files already present before startup
- [x] Run the new directory-handler test
- [x] Add permanent tests for .DS_Store and ordinary files
- [x] Test the startup scan with existing files, subfolders, and .DS_Store
- [x] Handle files moved into the watched folder using on_moved
- [x] Add a test for filenames similar to .DS_Store
- [x] Skip temporary download extensions in event handlers and startup scans
- [x] Test temporary downloads and organization after the final rename
- [x] Move the Python package and tests into backend/
- [x] Create frontend/ with its own README
- [x] Keep shared architecture documentation in root docs/
- [x] Update CI and README commands for the backend location
- [x] Verify the relocated package imports and all 19 tests pass
- [x] Document first-version scope and user flows in docs/product.md
- [x] Add a file-signature helper to detect changes
- [x] Add a readiness tracker that measures how long a file stays unchanged
- [x] Test readiness timing, changes resetting the timer, and clearing tracked files
- [x] Queue created and moved files for readiness checks
- [x] Recheck pending files in the processing loop
- [x] Test delayed organization and changes resetting the waiting period
- [x] Update event-handler tests for queued processing
- [x] Connect startup scanning to the readiness queue and verify integration
- [x] Restore the startup-scan test for temporary downloads
- [x] Test duplicate events, disappearing files, and retries after move failures
- [x] Verify readiness behavior with 31 tests and a manual background-service check
- [x] Document queued processing and readiness limitations in architecture.md
- [x] Validate config.yaml at startup with clear ConfigError messages
- [x] Reject a watch folder that is the same as, or inside, the destination
- [x] Test missing, empty, and invalid configs plus a valid config (38 tests pass)
- [x] Sort multi-part extensions like .tar.gz correctly (longest match wins; 41 tests pass)
- [x] Choose Tauri + React + TypeScript for the frontend (ADR 001)
- [x] Scaffold the Tauri app in frontend/
- [x] Design frontend/backend communication and process ownership (ADR 002)


## Next
- [ ] Add the backend HTTP API with start/stop/status (see ADR 002)
- [ ] Document file-safety requirements and error behavior
- [ ] Build the frontend status screen and connect it to the backend
- [ ] Record a short demo GIF for the README

## Later / optional
- [ ] AI-based smart naming (reads file content, not just filename)
- [ ] Tray/menu-bar app instead of a background script
- [ ] Undo/history so a bad auto-move is reversible
- [ ] Build a macOS menu-bar interface with start/stop controls
- [ ] Package the organizer as a standalone macOS .app

## Known limitations
- A file remaining unchanged for three seconds does not guarantee writing
  has finished; a paused download may resume later.
- `clean_filename()` still treats only the last extension as the extension, so
  `backup.tar.gz` is renamed `Backup.Tar.gz`. Cosmetic; it is sorted correctly.
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
- Config validation added in config.py; __main__.py exits cleanly on bad config.
- All 38 automated tests pass.

## Next session
- Review and commit the startup-readiness integration, tests, and documentation.
- Choose the frontend framework and document the decision.
- Define frontend/backend communication and process ownership.
- Document file-safety requirements before implementing frontend controls.
