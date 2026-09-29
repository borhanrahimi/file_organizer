# 001: Frontend framework

## Status

Accepted (2026-09-29)

## Context

File Organizer has a working Python backend that watches a folder and sorts
files. Everyday use still requires terminal commands and a hand-written config
file. The first frontend must let a user:

- See whether the organizer is running, stopped, or needs attention.
- Start and stop organization.
- Choose a source and destination folder with the system folder picker.
- See recent moves and understandable errors.
- Open the destination folder in the system file manager.

The app should run on macOS, Windows, and Linux. The backend already uses
cross-platform libraries (`pathlib`, `watchdog`), but it is currently started
through a macOS-only LaunchAgent.

This is also a learning project, so the choice should teach transferable skills.

## Options considered

### Tauri with React and TypeScript

- Pros: runs on macOS, Windows, and Linux from one codebase. Uses the
  operating system's built-in web view, so the app is small compared with
  Electron. Provides native folder pickers and "open in file manager" through
  plugins. React and TypeScript are widely used, well documented skills.
- Cons: three languages in one project (Python, TypeScript, a little Rust).
  Tauri does not include Python; the backend must be packaged as a separate
  executable (a "sidecar") for each platform. Each platform's web view can
  render slightly differently.

### PySide6 (Qt for Python)

- Pros: same language as the backend. Native folder pickers and a
  system tray icon are built in. Cross-platform.
- Cons: Qt skills transfer less widely than web skills. Bundled apps are large.
  PySide6 is licensed under the LGPL, which adds conditions when distributing.

### Electron with React

- Pros: cross-platform, very large ecosystem, same web skills as Tauri.
- Cons: bundles a full Chromium browser, so apps are much larger and use more
  memory. Still needs a separately packaged Python backend.

### SwiftUI

- Pros: the most native macOS experience.
- Cons: macOS only, which conflicts with the cross-platform goal. Requires
  learning Swift and bridging to Python.

## Decision

We will build the frontend with **Tauri 2, React, and TypeScript** in
`frontend/`.

The Python backend stays responsible for validation and all file operations.
The frontend only displays information and sends requests.

## Consequences

- Easier: one frontend codebase for all three desktop platforms; a modern,
  well-documented UI stack; a small app bundle.
- Harder: the project now needs Rust and Node.js installed to build the
  frontend, and CI will need extra steps.
- The macOS LaunchAgent cannot be the only way to run the backend. The Tauri
  app will likely start and stop the backend itself on every platform. This
  must be decided in the frontend/backend communication design.
- The backend must be packaged as a standalone executable per platform
  (for example with PyInstaller) before the app can be distributed.
- The app must be tested on each platform it claims to support; working on
  macOS does not prove it works on Windows or Linux.
