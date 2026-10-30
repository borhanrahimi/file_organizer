import threading
import time

import pytest

from organizer.config import ConfigError, load_config
from organizer.lock import LockHeldError, OrganizerLock
from organizer.service import OrganizerRunningError, OrganizerService


def wait_until(condition, timeout=2.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if condition():
            return True
        time.sleep(0.01)
    return False


def make_folders(tmp_path):
    watch = tmp_path / "downloads"
    watch.mkdir()
    return watch, tmp_path / "organized"


def make_service(tmp_path, watch=None):
    kwargs = {} if watch is None else {"watch": watch}
    return OrganizerService(
        tmp_path / "settings.yaml", tmp_path / "organizer.lock", **kwargs
    )


def test_new_service_is_stopped_with_no_folders(tmp_path):
    service = make_service(tmp_path)

    assert service.status() == {"state": "stopped", "message": None}
    settings = service.settings()
    assert settings["watch_folder"] is None
    assert settings["destination_root"] is None
    assert "Images" in settings["categories"]


def test_start_without_folders_raises_config_error(tmp_path):
    service = make_service(tmp_path)

    with pytest.raises(ConfigError, match="watch_folder"):
        service.start()
    assert service.status()["state"] == "stopped"


def test_update_settings_saves_and_returns_them(tmp_path):
    watch, destination = make_folders(tmp_path)
    service = make_service(tmp_path)

    saved = service.update_settings(str(watch), str(destination))

    assert saved["watch_folder"] == str(watch.resolve())
    assert saved["destination_root"] == str(destination.resolve())
    assert service.settings() == saved
    assert load_config(tmp_path / "settings.yaml")[0] == str(watch.resolve())


def test_settings_are_read_back_by_a_new_service(tmp_path):
    watch, destination = make_folders(tmp_path)
    make_service(tmp_path).update_settings(str(watch), str(destination))

    assert make_service(tmp_path).settings()["watch_folder"] == str(watch.resolve())


def test_invalid_settings_are_rejected_and_not_saved(tmp_path):
    service = make_service(tmp_path)

    with pytest.raises(ConfigError, match="not an existing folder"):
        service.update_settings(str(tmp_path / "missing"), str(tmp_path / "out"))

    assert not (tmp_path / "settings.yaml").exists()
    assert service.settings()["watch_folder"] is None


def test_broken_settings_file_reports_error(tmp_path):
    (tmp_path / "settings.yaml").write_text("watch_folder: [unclosed")

    service = make_service(tmp_path)

    status = service.status()
    assert status["state"] == "error"
    assert "not valid YAML" in status["message"]


def test_start_and_stop_real_watcher(tmp_path):
    watch, destination = make_folders(tmp_path)
    service = make_service(tmp_path)
    service.update_settings(str(watch), str(destination))

    assert service.start() == {"state": "running", "message": None}
    assert service._thread.is_alive()

    assert service.stop() == {"state": "stopped", "message": None}
    assert service._thread is None


def test_running_watcher_organizes_and_records_a_file(tmp_path):
    watch, destination = make_folders(tmp_path)
    service = make_service(tmp_path)
    service.update_settings(str(watch), str(destination))
    service.start()

    try:
        (watch / "notes.txt").write_text("hello")
        organized = destination / "Documents" / "Notes.txt"
        assert wait_until(organized.exists, timeout=8)
        assert organized.read_text() == "hello"
        assert wait_until(lambda: service.activity.events(), timeout=2)
        assert service.activity.events()[0]["type"] == "moved"
    finally:
        service.stop()


def test_start_twice_and_stop_twice_change_nothing(tmp_path):
    watch, destination = make_folders(tmp_path)
    service = make_service(tmp_path)
    service.update_settings(str(watch), str(destination))

    service.start()
    first_thread = service._thread
    assert service.start() == {"state": "running", "message": None}
    assert service._thread is first_thread

    service.stop()
    assert service.stop() == {"state": "stopped", "message": None}


def test_settings_cannot_change_while_running(tmp_path):
    watch, destination = make_folders(tmp_path)
    service = make_service(tmp_path)
    service.update_settings(str(watch), str(destination))
    service.start()

    try:
        with pytest.raises(OrganizerRunningError, match="Stop the organizer"):
            service.update_settings(str(watch), str(tmp_path / "elsewhere"))
    finally:
        service.stop()


def test_start_is_refused_while_another_organizer_holds_the_lock(tmp_path):
    watch, destination = make_folders(tmp_path)
    service = make_service(tmp_path)
    service.update_settings(str(watch), str(destination))

    other = OrganizerLock(tmp_path / "organizer.lock")
    other.acquire()
    try:
        with pytest.raises(LockHeldError, match="already running"):
            service.start()
        assert service.status()["state"] == "stopped"
    finally:
        other.release()

    service.start()
    service.stop()


def test_lock_is_released_after_stop(tmp_path):
    watch, destination = make_folders(tmp_path)
    service = make_service(tmp_path)
    service.update_settings(str(watch), str(destination))
    service.start()
    service.stop()

    other = OrganizerLock(tmp_path / "organizer.lock")
    other.acquire()
    other.release()


def test_crashed_watcher_reports_error_and_can_restart(tmp_path):
    watch, destination = make_folders(tmp_path)
    crashes = []

    def crash_once(watch_folder, destination_root, categories, stop_event, activity):
        if not crashes:
            crashes.append(True)
            raise OSError("Folder disappeared")
        stop_event.wait()

    service = make_service(tmp_path, watch=crash_once)
    service.update_settings(str(watch), str(destination))
    service.start()

    assert wait_until(lambda: service.status()["state"] == "error")
    assert service.status()["message"] == (
        "The organizer stopped unexpectedly: Folder disappeared"
    )

    assert service.start() == {"state": "running", "message": None}
    assert service._thread.is_alive()
    service.stop()
    assert service.status() == {"state": "stopped", "message": None}


def test_stop_waits_for_the_watcher_to_finish(tmp_path):
    watch, destination = make_folders(tmp_path)
    finished = threading.Event()

    def slow_watch(watch_folder, destination_root, categories, stop_event, activity):
        stop_event.wait()
        time.sleep(0.2)
        finished.set()

    service = make_service(tmp_path, watch=slow_watch)
    service.update_settings(str(watch), str(destination))
    service.start()
    service.stop()

    assert finished.is_set()
