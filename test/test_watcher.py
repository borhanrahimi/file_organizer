from watchdog.events import DirCreatedEvent, FileCreatedEvent
from organizer.watcher import DownloadHandler

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

def test_handler_ignores_ds_store(tmp_path):
    source_file = tmp_path / ".DS_Store"
    source_file.touch()

    destination = tmp_path / "organized"
    handler = DownloadHandler(destination,{"Images": [".jpg"]})

    handler.on_created(FileCreatedEvent(str(source_file)))

    assert source_file.exists()
    assert not destination.exists()

def test_handler_organizes_created_file(tmp_path):
    source_file = tmp_path / "holiday photo.webp"
    source_file.write_text("dummy content")

    destination = tmp_path / "organized"
    handler = DownloadHandler(destination, {"Images": [".webp"]})

    handler.on_created(FileCreatedEvent(str(source_file)))

    organized_file = destination / "Images" / "Holiday_Photo.webp"
    assert organized_file.read_bytes() == b"dummy content"
    assert not source_file.exists()