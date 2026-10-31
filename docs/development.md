# Development guide

How to run File Organizer from source, test it, and build a release. For how
the code is organized, see the [architecture overview](architecture.md).

- [Requirements](#requirements)
- [Set up](#set-up)
- [Run](#run)
- [Test](#test)
- [Project structure](#project-structure)
- [Build the macOS app](#build-the-macos-app)
- [Release a new version](#release-a-new-version)

## Requirements

| Tool | Version | Needed for |
|---|---|---|
| Python | 3.10+ (CI uses 3.13) | Everything |
| Node.js | 20+ (CI uses 22) | Desktop app |
| Rust | stable | Desktop app ([Tauri prerequisites](https://tauri.app/start/prerequisites/)) |

macOS is the tested platform. Windows and Linux are supported by the code
but not yet tested by hand.

## Set up

```bash
git clone https://github.com/borhanrahimi/file_organizer.git
cd file_organizer
python3 -m pip install -e ./backend
python3 -m pip install pytest httpx      # for the tests
```

## Run

### Quick demo

Sorts sample files in a new temporary folder and prints the result. It never
touches your own files.

```bash
python3 -m organizer.demo
```

### Desktop app

```bash
cd frontend
npm install
npm run tauri dev
```

In development the app runs the backend with `python3 -m organizer.server`,
so backend changes take effect on the next launch. To use another Python,
such as a virtual environment's, set `ORGANIZER_PYTHON`:

```bash
ORGANIZER_PYTHON=../.venv/bin/python npm run tauri dev
```

The app stores its settings in
`~/Library/Application Support/com.borhan.file-organizer/settings.yaml`.

### Terminal mode

Runs without the app, using `config.yaml` in the current folder:

```bash
cp config.example.yaml config.yaml    # then edit it
python3 -m organizer
```

```yaml
watch_folder: "~/Downloads"
destination_root: "~/Organized"
categories:
  Images: [.jpg, .png]
  Documents: [.pdf, .docx]
  Archives: [.zip, .tar.gz]
```

`config.yaml` is personal and ignored by Git. To run terminal mode at login
on macOS, see [Running in the background on macOS](macos-launchagent.md).

### API server only

```bash
ORGANIZER_TOKEN=dev-secret python3 -m organizer.server --port 8000
curl -H "Authorization: Bearer dev-secret" http://127.0.0.1:8000/status
```

The endpoints and error codes are listed in
[architecture.md](architecture.md#http-api-apipy).

## Test

```bash
python3 -m pytest backend/test -v           # backend: 91 tests

cd frontend
npm run build                               # TypeScript type-check and build
(cd src-tauri && cargo test)                # app starts and stops the backend
```

The Rust tests start the real backend, so the Python package must be
installed first. CI runs the backend tests and the frontend build on every
push and pull request.

## Project structure

```text
backend/
  src/organizer/
    core.py         categorize, clean names, move without overwriting
    watcher.py      filesystem events and the processing loop
    readiness.py    wait until a file stops changing
    service.py      owns the watcher thread, state, and settings
    api.py          local HTTP API (FastAPI)
    server.py       runs the API; exits with its parent app
    activity.py     last 100 moves and errors
    lock.py         one organizer at a time
    config.py       load, validate, and save settings
    demo.py         try it on sample files
    __main__.py     terminal mode
  packaging/        entry point for the packaged backend
  test/             pytest suite
frontend/
  src/              React interface and API client
  src-tauri/        Rust: starts and stops the backend
  scripts/          packages the backend for release builds
docs/               user guide, architecture, decisions (ADRs)
```

## Build the macOS app

```bash
cd frontend
npm run release
```

This packages the backend into one executable with PyInstaller (in its own
virtual environment, so your Python is not changed), then builds:

- `src-tauri/target/release/bundle/macos/File Organizer.app`
- `src-tauri/target/release/bundle/dmg/File Organizer_<version>_aarch64.dmg`

The build is for the Mac it runs on (Apple silicon on Apple silicon). See
[Packaging](architecture.md#packaging) for how the pieces fit together.

## Release a new version

1. Set the same version in all four files:
   - `frontend/src-tauri/tauri.conf.json` (this one names the release)
   - `frontend/src-tauri/Cargo.toml`
   - `frontend/package.json`
   - `backend/pyproject.toml`
2. Add the changes to [CHANGELOG.md](../CHANGELOG.md).
3. Commit and push.
4. Tag the commit and push the tag:

   ```bash
   git tag v1.1.0
   git push origin v1.1.0
   ```

5. The **Release** workflow checks that the tag matches the version, builds
   the `.dmg`, and creates a **draft** GitHub Release with the notes from
   `.github/release-notes.md`.
6. On GitHub, open **Releases**, review the draft, and click **Publish
   release**.

If the version check fails, fix the version, commit, and move the tag:

```bash
git tag -d v1.1.0 && git push origin :refs/tags/v1.1.0
git tag v1.1.0 && git push origin v1.1.0
```

Only move a tag if its release was never published.
