from watchdog.events import DirCreatedEvent
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

