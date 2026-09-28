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

## Next
- [ ] Connect startup scanning to the readiness queue and verify integration
- [ ] Choose the frontend framework and document the decision
- [ ] Document frontend/backend communication and process ownership
- [ ] Document file-safety requirements and error behavior
- [ ] Restore the startup-scan test for temporary downloads
- [ ] Add backend configuration validation and start/stop/status controls
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
- Permanent tests cover directory events, .DS_Store, and ordinary files.
- The startup scan is implemented, tested, and connected to start_watching().
- All tests passed.
- on_moved handles files using event.dest_path.
- Tests for moved files and ignoring moved .DS_Store files pass.
- Temporary download extensions are skipped by both event handlers and the startup scan.
- Tests cover temporary downloads and organization after the final rename.
- The similarly named .DS_Store file test passes.

- Created and moved files now wait for stability before organization.
- All 27 tests pass.
- Startup scanning still moves existing files immediately.
- Watcher and test changes committed as 7c8dc3a.

## Next session
- Change the startup scan to queue existing files.
- Update the startup-scan test for delayed organization.
- Restore startup coverage for temporary downloads.
- Test duplicate events, disappearing files, and retries after move failures.
- Run the full suite before restarting and manually testing the service.