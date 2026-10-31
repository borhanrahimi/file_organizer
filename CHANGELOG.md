# Changelog

All notable changes to this project are listed here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow
[Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.0.0] - 2026-10-30

First release.

### Added

- Desktop app for macOS (Apple silicon): choose a source and destination
  folder, start and stop the organizer, and see recent moves and errors.
- Downloadable `.dmg` that includes its own backend; Python is not needed.
- Real-time sorting into Images, Documents, Videos, Music, Archives, and
  Others, including subfolders and files already in the folder.
- Filename cleanup, and numbered names instead of overwriting existing files.
- Waits for downloads to finish: skips `.crdownload`, `.part`, and `.download`
  files, and moves a file only after it stops changing for three seconds.
- Only one organizer runs at a time, across the app, terminal mode, and the
  macOS LaunchAgent.
- Terminal mode (`python3 -m organizer`) configured with `config.yaml`.
- `python3 -m organizer.demo` to try it on sample files.
- Local HTTP API used by the app, available only on `127.0.0.1` with a
  per-launch token.

[Unreleased]: https://github.com/borhanrahimi/file_organizer/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/borhanrahimi/file_organizer/releases/tag/v1.0.0
