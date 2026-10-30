import pytest

from organizer.lock import LockHeldError, OrganizerLock


def test_second_lock_on_same_file_is_refused(tmp_path):
    lock_path = tmp_path / "data" / "organizer.lock"
    first = OrganizerLock(lock_path)
    second = OrganizerLock(lock_path)

    first.acquire()
    try:
        with pytest.raises(LockHeldError, match="already running"):
            second.acquire()
    finally:
        first.release()


def test_lock_can_be_taken_again_after_release(tmp_path):
    lock_path = tmp_path / "organizer.lock"
    first = OrganizerLock(lock_path)
    second = OrganizerLock(lock_path)

    first.acquire()
    first.release()
    second.acquire()
    second.release()


def test_acquire_and_release_are_safe_to_repeat(tmp_path):
    lock = OrganizerLock(tmp_path / "organizer.lock")

    lock.acquire()
    lock.acquire()
    lock.release()
    lock.release()

    other = OrganizerLock(tmp_path / "organizer.lock")
    other.acquire()
    other.release()
