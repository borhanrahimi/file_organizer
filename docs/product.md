# Product Plan

## Purpose

Help a macOS user organize files automatically through a simple
desktop interface, without needing terminal commands for everyday use.

## Current status

The Python backend, its local HTTP API, and the first version of the desktop
app are implemented. The app runs from source (`npm run tauri dev`) and needs
Python with the backend installed; a standalone packaged app is future work.

## First-version features

- Show whether the organizer is running, stopped, or needs attention.
- Start and stop organization.
- Choose one source folder and one destination folder.
- Display the configured file categories.
- Show recent successful moves and errors.
- Show the destination folder in Finder (or the system file manager).
- Cross-platform support.


## First-time setup

1. Choose the source folder.
2. Choose the destination folder.
3. Review the categories and organization behavior.
4. Explain that existing files and files in subfolders will be processed.
5. Start only after the user explicitly chooses Start.

## Everyday use

The user can check status, view recent activity, and stop organization.

Stopping prevents new work from starting; an in-progress move may finish.
Closing the window quits the app and stops the organizer. The window says so
next to the Start button.

## Safety expectations

- Validate settings before starting.
- Prevent unsafe source/destination overlap.
- Avoid moving files that are still being written.
- Preserve file contents and handle filename collisions.
- Show actionable errors without claiming failed operations succeeded.
- Keep file processing local; no cloud upload is planned.

See "File-safety requirements" in [architecture.md](architecture.md) for
how each one is enforced and what is not guaranteed.

## Deferred features

- AI naming.
- Undo and restore history.
- Multiple watched folders.
- Editing category rules through the interface.
- Cloud synchronization.

## First-version completion criteria

- A user can configure and operate the app without terminal commands.
- Status reflects the actual backend state.
- File operations and failure cases have automated tests.
- The complete application passes manual checks in a test folder.
- Setup, permissions, limitations, and recovery steps are documented.