import time 
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from organizer.core import organize_file

class DownloadHandler(FileSystemEventHandler):
    def __init__(self, destination_root, categories):
        self.destination_root = destination_root
        self.categories = categories
    
    def on_created(self, event):
        if event.is_directory:
            return
        
        if Path(event.src_path).name == (".DS_Store"):
            return
        
        organize_file(event.src_path, self.destination_root, self.categories)

def start_watching(watch_folder, destination_root, categories):
    observer = Observer()
    observer.schedule(
        DownloadHandler(destination_root, categories), 
        watch_folder, 
        recursive=True)
    observer.start()

    print(f"Watching folder: {watch_folder}...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()