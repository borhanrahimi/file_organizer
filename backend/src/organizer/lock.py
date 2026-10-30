import os
import sys
from pathlib import Path

APP_FOLDER_NAME = "File Organizer"


class LockHeldError(Exception):
    """Raised when another organizer already holds the lock file."""


def default_data_folder():
    """Return the per-user application data folder for this platform."""
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / APP_FOLDER_NAME
    if sys.platform == "win32":
        base = os.environ.get("APPDATA") or Path.home() / "AppData" / "Roaming"
        return Path(base) / APP_FOLDER_NAME
    base = os.environ.get("XDG_STATE_HOME") or Path.home() / ".local" / "state"
    return Path(base) / "file-organizer"


def default_lock_path():
    return default_data_folder() / "organizer.lock"


class OrganizerLock:
    """An exclusive lock that the operating system releases if the process dies."""

    def __init__(self, path):
        self.path = Path(path)
        self._file = None

    def acquire(self):
        if self._file is not None:
            return

        self.path.parent.mkdir(parents=True, exist_ok=True)
        lock_file = open(self.path, "a+")

        try:
            _lock(lock_file)
        except OSError:
            lock_file.close()
            raise LockHeldError(
                "Another file organizer is already running "
                f"(lock file: {self.path}). Stop it first."
            )

        self._file = lock_file

    def release(self):
        if self._file is None:
            return

        _unlock(self._file)
        self._file.close()
        self._file = None


if sys.platform == "win32":
    import msvcrt

    def _lock(lock_file):
        lock_file.seek(0)
        msvcrt.locking(lock_file.fileno(), msvcrt.LK_NBLCK, 1)

    def _unlock(lock_file):
        lock_file.seek(0)
        msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
else:
    import fcntl

    def _lock(lock_file):
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

    def _unlock(lock_file):
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
