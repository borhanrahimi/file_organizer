# Security

## Supported versions

Security fixes are made for the latest release.

## Reporting a problem

Please do not open a public issue for a security problem. Instead, report it
privately through GitHub:
[Report a vulnerability](https://github.com/borhanrahimi/file_organizer/security/advisories/new).

Include what you found, how to reproduce it, and what an attacker could do.
You can expect a first reply within a week.

## Security model

File Organizer moves files on your computer, so it is designed to be reachable
only by its own app window:

- The backend listens on `127.0.0.1` only, never on the network.
- The app creates a new random token at every launch and passes it to the
  backend in an environment variable. Every request must include it.
- Only the app window's origins are allowed to call the API from a browser
  context, so websites cannot control it.
- Folder settings are validated by the backend on every change and before
  every start.
- No data leaves your computer, and no shell commands are built from user
  input.

Known limitation: the macOS app is not code-signed or notarized.
