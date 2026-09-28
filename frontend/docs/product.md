# Product Plan

## Purpose

Help a macOS user organize files automatically through a simple
desktop interface, without needing terminal commands for everyday use.

## Current status

The Python backend is implemented.
The desktop frontend is planned.
File-readiness checks and other safety improvements remain unfinished.

## First-version features

- Show whether the organizer is running, stopped, or needs attention.
- Start and stop organization.
- Choose one source folder and one destination folder.
- Display the configured file categories.
- Show recent successful moves and errors.
- Open the destination folder in Finder.

## First-time setup

1. Choose the source folder.
2. Choose the destination folder.
3. Review the categories and organization behavior.
4. Explain that existing files and files in subfolders will be processed.
5. Start only after the user explicitly chooses Start.

## Everyday use

The user can check status, view recent activity, and stop organization.

Stopping prevents new work from starting; an in-progress move may finish.
Closing the interface and stopping the organizer must have clearly
documented behavior before implementation.

## Safety expectations

- Validate settings before starting.
- Prevent unsafe source/destination overlap.
- Avoid moving files that are still being written.
- Preserve file contents and handle filename collisions.
- Show actionable errors without claiming failed operations succeeded.
- Keep file processing local; no cloud upload is planned.

These are requirements, not claims that all protections exist today.

## Deferred features

- AI naming.
- Undo and restore history.
- Multiple watched folders.
- Editing category rules through the interface.
- Cross-platform support.
- Cloud synchronization.

## First-version completion criteria

- A user can configure and operate the app without terminal commands.
- Status reflects the actual backend state.
- File operations and failure cases have automated tests.
- The complete application passes manual checks in a test folder.
- Setup, permissions, limitations, and recovery steps are documented.