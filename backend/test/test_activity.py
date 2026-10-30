from datetime import datetime, timezone

from organizer.activity import ActivityLog
from organizer.readiness import FileReadinessTracker
from organizer.watcher import DownloadHandler


def fixed_clock():
    return datetime(2026, 10, 30, 12, 0, 0, tzinfo=timezone.utc)


def test_events_are_newest_first():
    activity = ActivityLog(clock=fixed_clock)

    activity.record_move("/in/a.jpg", "/out/Images/A.jpg")
    activity.record_error("/in/b.pdf", "Could not move file: denied")

    assert activity.events() == [
        {
            "timestamp": "2026-10-30T12:00:00+00:00",
            "type": "error",
            "source": "/in/b.pdf",
            "message": "Could not move file: denied",
        },
        {
            "timestamp": "2026-10-30T12:00:00+00:00",
            "type": "moved",
            "source": "/in/a.jpg",
            "destination": "/out/Images/A.jpg",
        },
    ]


def test_only_most_recent_events_are_kept():
    activity = ActivityLog(max_events=3, clock=fixed_clock)

    for number in range(5):
        activity.record_move(f"/in/{number}.jpg", f"/out/{number}.jpg")

    sources = [event["source"] for event in activity.events()]
    assert sources == ["/in/4.jpg", "/in/3.jpg", "/in/2.jpg"]


def test_default_limit_is_100_events():
    activity = ActivityLog(clock=fixed_clock)

    for number in range(150):
        activity.record_move(f"/in/{number}.jpg", f"/out/{number}.jpg")

    events = activity.events()
    assert len(events) == 100
    assert events[0]["source"] == "/in/149.jpg"


def test_handler_records_successful_move(tmp_path):
    source_file = tmp_path / "photo.webp"
    source_file.write_text("photo content")
    destination = tmp_path / "organized"

    now = [0.0]
    activity = ActivityLog(clock=fixed_clock)
    handler = DownloadHandler(
        destination,
        {"Images": [".webp"]},
        readiness=FileReadinessTracker(clock=lambda: now[0]),
        activity=activity,
    )

    handler.queue_file(source_file)
    handler.process_pending()
    assert activity.events() == []

    now[0] = 3.0
    handler.process_pending()

    assert activity.events() == [
        {
            "timestamp": "2026-10-30T12:00:00+00:00",
            "type": "moved",
            "source": str(source_file.resolve()),
            "destination": str(destination / "Images" / "Photo.webp"),
        }
    ]


def test_handler_records_failed_move(tmp_path, monkeypatch):
    from organizer import watcher

    source_file = tmp_path / "photo.webp"
    source_file.write_text("photo content")

    def always_fail(filepath, destination_root, categories):
        raise PermissionError("Simulated failure")

    monkeypatch.setattr(watcher, "organize_file", always_fail)

    now = [0.0]
    activity = ActivityLog(clock=fixed_clock)
    handler = DownloadHandler(
        tmp_path / "organized",
        {"Images": [".webp"]},
        readiness=FileReadinessTracker(clock=lambda: now[0]),
        activity=activity,
    )

    handler.queue_file(source_file)
    handler.process_pending()
    now[0] = 3.0
    handler.process_pending()

    assert activity.events() == [
        {
            "timestamp": "2026-10-30T12:00:00+00:00",
            "type": "error",
            "source": str(source_file.resolve()),
            "message": "Could not move file: Simulated failure",
        }
    ]
    assert source_file.exists()
