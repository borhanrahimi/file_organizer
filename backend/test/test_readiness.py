from organizer.readiness import get_file_signature, FileReadinessTracker


def test_unchanged_file_has_same_signature(tmp_path):
    filepath = tmp_path / "photo.webp"
    filepath.write_bytes(b"photo content")

    first = get_file_signature(filepath)
    second = get_file_signature(filepath)

    assert first is not None
    assert second == first


def test_growing_file_changes_signature(tmp_path):
    filepath = tmp_path / "photo.webp"
    filepath.write_bytes(b"partial")

    before = get_file_signature(filepath)

    with filepath.open("ab") as file:
        file.write(b" more content")

    after = get_file_signature(filepath)

    assert before is not None
    assert after is not None
    assert after != before


def test_missing_file_returns_none(tmp_path):
    assert get_file_signature(tmp_path / "missing.webp") is None


def test_directory_returns_none(tmp_path):
    assert get_file_signature(tmp_path) is None

def test_file_becomes_ready_after_stable_period(tmp_path):
    filepath = tmp_path / "photo.webp"
    filepath.write_bytes(b"content")

    now = [0.0]
    tracker = FileReadinessTracker(clock=lambda: now[0])

    assert tracker.is_ready(filepath) is False

    now[0] = 2.0
    assert tracker.is_ready(filepath) is False

    now[0] = 3.0
    assert tracker.is_ready(filepath) is True


def test_file_change_restarts_waiting_period(tmp_path):
    filepath = tmp_path / "photo.webp"
    filepath.write_bytes(b"partial")

    now = [0.0]
    tracker = FileReadinessTracker(clock=lambda: now[0])

    assert tracker.is_ready(filepath) is False

    now[0] = 2.0
    filepath.write_bytes(b"more content arrived")
    assert tracker.is_ready(filepath) is False

    now[0] = 3.0
    assert tracker.is_ready(filepath) is False

    now[0] = 5.0
    assert tracker.is_ready(filepath) is True


def test_forget_requires_a_new_waiting_period(tmp_path):
    filepath = tmp_path / "photo.webp"
    filepath.write_bytes(b"content")

    now = [0.0]
    tracker = FileReadinessTracker(clock=lambda: now[0])

    assert tracker.is_ready(filepath) is False

    now[0] = 3.0
    assert tracker.is_ready(filepath) is True

    tracker.forget(filepath)

    assert tracker.is_ready(filepath) is False