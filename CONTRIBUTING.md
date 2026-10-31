# Contributing

Thanks for your interest in File Organizer. Bug reports, ideas, and pull
requests are welcome.

## Reporting a bug or suggesting a feature

[Open an issue](https://github.com/borhanrahimi/file_organizer/issues/new/choose)
and pick the bug report or feature request template. For a bug, the most
helpful details are what you did, what you expected, what happened, any
message shown in the app, and your macOS version.

For security problems, follow [SECURITY.md](SECURITY.md) instead of opening a
public issue.

## Making a change

1. Set up the project with the [development guide](docs/development.md).
2. Create a branch from `main`.
3. Write or update a test first, then the code. Tests compare against a
   specific expected value, and a test should fail for the reason it is
   checking.
4. Run the checks:

   ```bash
   python3 -m pytest backend/test
   cd frontend && npm run build
   ```

5. Update the docs if behavior changes, and add a line under
   **Unreleased** in [CHANGELOG.md](CHANGELOG.md).
6. Open a pull request that explains what changed and why.

## Guidelines

- **File safety comes first.** The backend must never overwrite or lose a
  file, and it enforces its rules even for requests from the app. See
  [File-safety requirements](docs/architecture.md#file-safety-requirements).
- **Keep changes small** and focused on one thing.
- **Commit messages** describe the change in the imperative mood, for
  example `Add GET /activity endpoint`.
- **Larger design changes** are recorded as a decision record in
  [docs/decisions/](docs/decisions/).
