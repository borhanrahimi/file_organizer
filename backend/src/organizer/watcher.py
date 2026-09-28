import time 
from queue import Empty, Queue
import logging
from organizer.readiness import FileReadinessTracker
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from organizer.core import organize_file

TEMP_DOWNLOAD_EXTENSIONS = {".crdownload", ".part", ".download"}

def is_temporary_file(filepath):
    return Path(filepath).suffix.lower() in TEMP_DOWNLOAD_EXTENSIONS

class DownloadHandler(FileSystemEventHandler):
    def __init__(self, destination_root, categories, readiness=None):
        self.destination_root = destination_root
        self.categories = categories
        self.readiness = (
            readiness if readiness is not None else FileReadinessTracker()
        )
        self.incoming = Queue()
        self.pending = set()

    def queue_file(self, filepath):
        path = Path(filepath).resolve()
        destination = Path(self.destination_root).resolve()

        if path.name == ".DS_Store":
            return
        if is_temporary_file(path):
            return
        if path.is_relative_to(destination):
            return
        if not path.is_file():
            return                  
        self.incoming.put(path)

    def process_pending(self):
        while True:
            try:
                path = self.incoming.get_nowait()
            except Empty:
                break

            self.pending.add(path)

        for path in list(self.pending):
            try:
                if not path.is_file():
                    self.pending.discard(path)
                    self.readiness.forget(path)
                    continue
                if not self.readiness.is_ready(path):
                    continue
                organize_file(
                    path,
                    self.destination_root,
                    self.categories,
                )
            except OSError:
                logging.exception("Could not organize file: %s", path)
                self.readiness.forget(path)
                continue

            self.pending.discard(path)
            self.readiness.forget(path)
    
    def on_created(self, event):
        if event.is_directory:
            return

        self.queue_file(event.src_path)

    def on_moved(self, event):
        if event.is_directory:
            return

        self.queue_file(event.dest_path)

def organize_existing_files(watch_folder, destination_root, categories):
    for filepath in Path(watch_folder).rglob('*'):
        if not filepath.is_file():
            continue
        if filepath.name == ".DS_Store":
            continue
        if filepath.resolve().is_relative_to(Path(destination_root).resolve()):
            continue
        if is_temporary_file(filepath):
            continue
        organize_file(filepath, destination_root, categories)

def start_watching(watch_folder, destination_root, categories):
    organize_existing_files(watch_folder, destination_root, categories)

    handler = DownloadHandler(destination_root, categories)

    observer = Observer()
    observer.schedule(handler, watch_folder, recursive=True)
    observer.start()

    print(f"Watching folder: {watch_folder}...")

    try:
        while True:
            handler.process_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        observer.stop()
        observer.join()