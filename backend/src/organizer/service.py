import logging
import threading
from pathlib import Path

from organizer.activity import ActivityLog
from organizer.config import (
    DEFAULT_CATEGORIES,
    ConfigError,
    read_config_file,
    save_config,
    validate_config,
)
from organizer.lock import OrganizerLock
from organizer.watcher import start_watching


class OrganizerRunningError(Exception):
    """Raised when an action needs the organizer to be stopped first."""


class OrganizerService:
    """Owns the watcher thread, its state, and the saved settings.

    Start, stop, and settings changes are serialized by one lock. A second,
    smaller lock protects the state that the watcher thread may also change.
    """

    def __init__(self, settings_path, lock_path, activity=None, watch=start_watching):
        self.settings_path = Path(settings_path)
        self.activity = activity if activity is not None else ActivityLog()
        self._watch = watch
        self._file_lock = OrganizerLock(lock_path)
        self._control_lock = threading.Lock()
        self._state_lock = threading.Lock()
        self._thread = None
        self._stop_event = None
        self._state = "stopped"
        self._message = None
        self._settings = self._read_settings()

    def _read_settings(self):
        settings = {
            "watch_folder": None,
            "destination_root": None,
            "categories": DEFAULT_CATEGORIES,
        }

        if not self.settings_path.exists():
            return settings

        try:
            config = read_config_file(self.settings_path)
        except ConfigError as error:
            self._state = "error"
            self._message = str(error)
            return settings

        for key in settings:
            if key in config:
                settings[key] = config[key]
        return settings

    def status(self):
        with self._state_lock:
            return {"state": self._state, "message": self._message}

    def settings(self):
        return dict(self._settings)

    def start(self):
        with self._control_lock:
            if self._thread is not None and self._thread.is_alive():
                return self.status()

            # The previous thread may have crashed; clean up before starting again.
            self._cleanup_stopped_thread()

            watch_folder, destination_root, categories = validate_config(self._settings)
            self._file_lock.acquire()

            stop_event = threading.Event()
            thread = threading.Thread(
                target=self._run,
                args=(watch_folder, destination_root, categories, stop_event),
                name="organizer-watcher",
                daemon=True,
            )
            self._thread = thread
            self._stop_event = stop_event
            self._set_state("running", None)
            thread.start()
            return self.status()

    def stop(self):
        with self._control_lock:
            if self._stop_event is not None:
                self._stop_event.set()
            # An in-progress move is allowed to finish.
            self._cleanup_stopped_thread()
            self._set_state("stopped", None)
            return self.status()

    def update_settings(self, watch_folder, destination_root):
        with self._control_lock:
            if self._thread is not None and self._thread.is_alive():
                raise OrganizerRunningError(
                    "Stop the organizer before changing settings."
                )

            watch_folder, destination_root, categories = validate_config({
                "watch_folder": watch_folder,
                "destination_root": destination_root,
                "categories": self._settings["categories"],
            })
            save_config(self.settings_path, watch_folder, destination_root, categories)
            self._settings = {
                "watch_folder": watch_folder,
                "destination_root": destination_root,
                "categories": categories,
            }
            # Saving valid settings clears an earlier settings or crash error.
            self._set_state("stopped", None)
            return self.settings()

    def _cleanup_stopped_thread(self):
        if self._thread is not None:
            self._thread.join()
        self._thread = None
        self._stop_event = None
        self._file_lock.release()

    def _run(self, watch_folder, destination_root, categories, stop_event):
        try:
            self._watch(
                watch_folder,
                destination_root,
                categories,
                stop_event=stop_event,
                activity=self.activity,
            )
        except Exception as error:
            logging.exception("The organizer stopped unexpectedly")
            self._set_state("error", f"The organizer stopped unexpectedly: {error}")
            return

        if not stop_event.is_set():
            self._set_state("stopped", None)

    def _set_state(self, state, message):
        with self._state_lock:
            self._state = state
            self._message = message
