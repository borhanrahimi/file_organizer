from watchdog.events import DirCreatedEvent, FileCreatedEvent, FileMovedEvent
from organizer.watcher import DownloadHandler, organize_existing_files  
from organizer.readiness import FileReadinessTracker

def test_handler_ignores_directories(tmp_path):

    source_folder= tmp_path / "holiday photos"
    source_folder.mkdir()

    photo = source_folder / "photo.jpg"
    photo.write_text("dummy content")

    destination = tmp_path / "organized"
    handler = DownloadHandler(destination,{"Images": [".jpg"]})

    handler.on_created(DirCreatedEvent(str(source_folder)))

    assert source_folder.is_dir()
    assert photo.read_text() == "dummy content"
    assert not destination.exists()
    assert handler.incoming.empty()

def test_handler_ignores_ds_store(tmp_path):
    source_file = tmp_path / ".DS_Store"
    source_file.touch()

    destination = tmp_path / "organized"
    handler = DownloadHandler(destination,{"Images": [".jpg"]})

    handler.on_created(FileCreatedEvent(str(source_file)))

    assert source_file.exists()
    assert not destination.exists()
    assert handler.incoming.empty()

def test_handler_organizes_created_file(tmp_path):
    source_file = tmp_path / "holiday photo.webp"
    source_file.write_text("dummy content")

    destination = tmp_path / "organized"

    now = [0.0]
    readiness = FileReadinessTracker(clock=lambda: now[0])
    handler = DownloadHandler(
        destination,
        {"Images": [".webp"]},
        readiness=readiness,
    )

    handler.on_created(FileCreatedEvent(str(source_file)))

    # Receiving the event must not move the file immediately.
    assert source_file.exists()
    assert not destination.exists()

    # The first check starts the stability timer.
    handler.process_pending()
    assert source_file.exists()
    assert not destination.exists()

    # After three unchanged seconds, the file can move.
    now[0] = 3.0
    handler.process_pending()

    organized_file = destination / "Images" / "Holiday_Photo.webp"
    assert organized_file.read_text() == "dummy content"
    assert not source_file.exists()


def test_scan_organizes_existing_files(tmp_path):
    source = tmp_path / "source"
    nested = source / "nested"
    nested.mkdir(parents=True)

    photo = source / "old photo.webp"
    photo.write_text("photo content")

    document = nested / "old notes.txt"
    document.write_text("notes content")

    metadata = source / ".DS_Store"
    metadata.touch()

    destination = tmp_path / "organized"
    categories = {
        "Images": [".webp"],
        "Documents": [".txt"],
    }

    organize_existing_files(source, destination, categories)

    assert (destination / "Images" / "Old_Photo.webp").read_text() == "photo content"
    assert (destination / "Documents" / "Old_Notes.txt").read_text() == "notes content"
    assert not photo.exists()
    assert not document.exists()
    assert metadata.exists()

def test_handler_organizes_moved_file(tmp_path):
    old_path = tmp_path / "old photo.webp"
    new_path = tmp_path / "holiday photo.webp"
    new_path.write_text("photo content")

    destination = tmp_path / "organized"

    now = [0.0]
    readiness = FileReadinessTracker(clock=lambda: now[0])
    handler = DownloadHandler(
        destination,
        {"Images": [".webp"]},
        readiness=readiness,
    )

    handler.on_moved(FileMovedEvent(str(old_path), str(new_path)))

    assert new_path.exists()
    assert not destination.exists()

    handler.process_pending()
    assert new_path.exists()
    assert not destination.exists()

    now[0] = 3.0
    handler.process_pending()

    organized_file = destination / "Images" / "Holiday_Photo.webp"
    assert organized_file.read_text() == "photo content"
    assert not new_path.exists()

def test_handler_ignores_moved_ds_store(tmp_path):
    old_path = tmp_path / "old metadata"
    new_path = tmp_path / ".DS_Store"
    new_path.touch()

    destination = tmp_path / "organized"
    handler = DownloadHandler(destination, {"Images": [".webp"]})

    handler.on_moved(FileMovedEvent(str(old_path), str(new_path)))

    assert new_path.exists()
    assert not destination.exists()
    assert handler.incoming.empty()

def test_handler_organizes_similarly_named_file(tmp_path):
    source_file = tmp_path / ".DS_Store.txt"
    source_file.write_text("keep this content")

    destination = tmp_path / "organized"

    now = [0.0]
    readiness = FileReadinessTracker(clock=lambda: now[0])
    handler = DownloadHandler(
        destination,
        {"Documents": [".txt"]},
        readiness=readiness,
    )

    handler.on_created(FileCreatedEvent(str(source_file)))

    handler.process_pending()
    assert source_file.exists()
    assert not destination.exists()

    now[0] = 3.0
    handler.process_pending()

    organized_file = destination / "Documents" / ".Ds_Store.txt"
    assert organized_file.read_text() == "keep this content"
    assert not source_file.exists()

def test_download_is_organized_after_completion(tmp_path):
    temporary_file = tmp_path / "holiday photo.webp.crdownload"
    temporary_file.write_text("photo content")

    destination = tmp_path / "organized"

    now = [0.0]
    readiness = FileReadinessTracker(clock=lambda: now[0])
    handler = DownloadHandler(
        destination,
        {"Images": [".webp"]},
        readiness=readiness,
    )

    handler.on_created(FileCreatedEvent(str(temporary_file)))

    # Temporary downloads must not enter the queue.
    assert handler.incoming.empty()
    assert temporary_file.exists()
    assert not destination.exists()

    completed_file = tmp_path / "holiday photo.webp"
    temporary_file.rename(completed_file)

    handler.on_moved(
        FileMovedEvent(str(temporary_file), str(completed_file))
    )

    # The final filename still needs a stability check.
    handler.process_pending()
    assert completed_file.exists()
    assert not destination.exists()

    now[0] = 3.0
    handler.process_pending()

    organized_file = destination / "Images" / "Holiday_Photo.webp"
    assert organized_file.read_text() == "photo content"
    assert not completed_file.exists()

def test_handler_ignores_moved_temporary_download(tmp_path):
    old_path = tmp_path / "previous.part"
    new_path = tmp_path / "photo.webp.part"
    new_path.write_text("unfinished content")

    destination = tmp_path / "organized"
    handler = DownloadHandler(destination, {"Images": [".webp"]})

    handler.on_moved(FileMovedEvent(str(old_path), str(new_path)))

    assert new_path.read_text() == "unfinished content"
    assert not destination.exists()
    assert handler.incoming.empty()

def test_pending_file_waits_until_stable(tmp_path):
    source_file = tmp_path / "holiday photo.webp"
    source_file.write_bytes(b"partial")

    destination = tmp_path / "organized"
    now = [0.0]
    readiness = FileReadinessTracker(clock=lambda: now[0])
    handler = DownloadHandler(
        destination,
        {"Images": [".webp"]},
        readiness=readiness,
    )

    handler.queue_file(source_file)
    handler.process_pending()

    assert source_file.exists()
    assert not destination.exists()

    # More data arrives, so the waiting period must restart.
    now[0] = 2.0
    source_file.write_bytes(b"complete photo content")
    handler.process_pending()

    now[0] = 3.0
    handler.process_pending()

    assert source_file.exists()
    assert not destination.exists()

    # The updated file has now stayed unchanged for three seconds.
    now[0] = 5.0
    handler.process_pending()

    organized_file = destination / "Images" / "Holiday_Photo.webp"
    assert organized_file.read_bytes() == b"complete photo content"
    assert not source_file.exists()
    assert not handler.pending