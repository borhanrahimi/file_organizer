<p align="center">
  <img src="frontend/app-icon.png" alt="" width="96">
</p>

<h1 align="center">File Organizer</h1>

<p align="center">
  Keeps your Downloads folder tidy on its own: it sorts new files into folders by type and cleans up their names.
</p>

<p align="center">
  <a href="https://github.com/borhanrahimi/file_organizer/releases/latest"><strong>Download for macOS</strong></a>
  ·
  <a href="docs/user-guide.md">User guide</a>
  ·
  <a href="docs/development.md">Build from source</a>
</p>

<p align="center">
  <a href="https://github.com/borhanrahimi/file_organizer/actions/workflows/tests.yaml"><img src="https://github.com/borhanrahimi/file_organizer/actions/workflows/tests.yaml/badge.svg" alt="Tests"></a>
  <a href="https://github.com/borhanrahimi/file_organizer/releases/latest"><img src="https://img.shields.io/github/v/release/borhanrahimi/file_organizer" alt="Latest release"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="MIT license"></a>
</p>

<p align="center">
  <img src="docs/demo.gif" alt="File Organizer sorting six new downloads into category folders" width="600">
</p>

## Features

- **Sorts files as they arrive** into Images, Documents, Videos, Music,
  Archives, and Others, including files in subfolders and files already there.
- **Cleans up names:** `final_report FINAL (2).docx` becomes
  `Final_Report_Final_2.docx`.
- **Never overwrites:** if a name is taken, the new file becomes `Report_1.pdf`.
- **Waits for downloads to finish** before moving anything.
- **Private:** everything runs on your computer. Nothing is uploaded.

## Get started

1. [Download the latest `.dmg`](https://github.com/borhanrahimi/file_organizer/releases/latest)
   (macOS, Apple silicon) and drag the app into Applications.
2. The first time, approve it in **System Settings → Privacy & Security →
   Open Anyway**. It is not signed with a paid Apple developer account.
3. Choose a source folder and a destination folder, then click **Start**.

See the [user guide](docs/user-guide.md) for details and troubleshooting.
Intel Macs, Windows, and Linux can [run it from source](docs/development.md).

## How it's built

A Tauri (Rust) desktop app with a React + TypeScript interface. It starts a
Python backend (FastAPI, watchdog) that listens only on `127.0.0.1` and
watches the folder. The backend is tested with pytest (91 tests), CI runs on
every push, and tagged versions are built and published automatically.

- **Safety:** settings are validated, files are never overwritten, half-finished
  downloads are left alone, and only one organizer can run at a time.
- **Security:** the local API needs a new random token on every launch and
  only accepts requests from the app's window.
- **Reliability:** the backend shuts down with the app, even if the app
  crashes.

Read the [architecture overview](docs/architecture.md) and the
[design decisions](docs/decisions/) for details.

## Documentation

| | |
|---|---|
| [User guide](docs/user-guide.md) | Install, use, troubleshoot, uninstall |
| [Development guide](docs/development.md) | Run from source, test, build, release |
| [Architecture](docs/architecture.md) | How the pieces fit together, API, safety rules |
| [Changelog](CHANGELOG.md) | What changed in each version |
| [Contributing](CONTRIBUTING.md) | How to report bugs and propose changes |
| [Security](SECURITY.md) | Security model and how to report a problem |

## License

[MIT](LICENSE) © 2026 Borhan Rahimi
