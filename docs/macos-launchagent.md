# Running in the background on macOS (LaunchAgent)

Terminal mode (`python3 -m organizer`) can run at login as a macOS
LaunchAgent. The desktop app does not need this; don't run both at once
(the organizer lock stops the second one from starting).

These commands manage the LaunchAgent named `com.borhan.file-organizer`.
They assume its configuration has already been saved to
`~/Library/LaunchAgents/com.borhan.file-organizer.plist`. This personal file
is outside the repository; installing the Python package does not create it.

The LaunchAgent must use your Python executable with the arguments
`-u`, `-m`, and `organizer`, set `WorkingDirectory` to your project root,
and set `RunAtLoad` to `true` to start at login. It reads the same
`config.yaml` as a manual run.

In the commands below, `$(id -u)` supplies your numeric user ID so
`launchctl` manages the job in your login session.

## Start and check status

Stop any terminal-run organizer with `Ctrl+C` first, so only one instance
watches the folder. If the background job is not already loaded, start it:

```bash
launchctl bootstrap "gui/$(id -u)" ~/Library/LaunchAgents/com.borhan.file-organizer.plist
```

Check its status:

```bash
launchctl print "gui/$(id -u)/com.borhan.file-organizer"
```

Look for `state = running`. If the job is not loaded, the status command
reports that it cannot find the service. If it is loaded but not running,
check the logs below.

## Stop the current job

```bash
launchctl bootout "gui/$(id -u)/com.borhan.file-organizer"
```

This stops and unloads the job. It can still start at your next login.
Running `bootout` on an already unloaded job reports an error.

## Disable or re-enable autostart

To prevent future startup, disable the job. If it is currently loaded,
also run `bootout` to stop it now:

```bash
launchctl disable "gui/$(id -u)/com.borhan.file-organizer"
launchctl bootout "gui/$(id -u)/com.borhan.file-organizer"
```

To re-enable autostart:

```bash
launchctl enable "gui/$(id -u)/com.borhan.file-organizer"
```

After enabling it, use the `bootstrap` command above to start it immediately
if it is not loaded, or let it start at your next login.

## Read the logs

With the configured log paths, read startup output and recent move messages
or errors using:

```bash
tail -n 20 ~/Library/Logs/file-organizer.log
tail -n 20 ~/Library/Logs/file-organizer-error.log
```

Python logging writes to standard error by default, so successful `INFO`
move messages also appear in `file-organizer-error.log`. Each move entry
records the timestamp, source path, and destination path. Log files appear
when the background job starts; if startup fails, check the error log.
