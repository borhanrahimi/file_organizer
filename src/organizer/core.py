import shutil
from pathlib import Path



CATEGORIES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp"],
    "Documents": [".pdf", ".docx", ".txt", ".xlsx"],
    "Videos": [".mp4", ".avi", ".mov"],
    "Music": [".mp3", ".wav", ".flac"],
    "Archives": [".zip", ".rar", ".tar.gz"]
}

# TODO: Path().suffix only grabs the last extension, so "file.tar.gz" becomes
# ".gz" not ".tar.gz" and won't match the Archives category correctly.
def get_category(filename):
    extension = Path(filename).suffix.lower()
    for category, extensions in CATEGORIES.items():
        if extension in extensions:
            return category
    return "Others"

# TODO: .title() capitalizes small words like "at"/"pm" oddly (e.g. "_At_11.42.53_Pm").
# Good enough for v1 — revisit if it becomes annoying.
def clean_filename(filename):
    stem = Path(filename).stem
    extension = Path(filename).suffix

    stem = stem.lower()
    stem = stem.title()
    stem = stem.replace(" ", "_")
    stem = stem.replace(")","")
    stem = stem.replace("(","")

    return stem + extension


def organize_file(filepath, destination_root):
    filename = Path(filepath).name
    category = get_category(filename)
    new_name = clean_filename(filename)
    destination_path = Path(destination_root) / category / new_name
    destination_path = unique_path(destination_path)

    destination_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(filepath, destination_path)

def unique_path(destination_path):
    if not destination_path.exists():
        return destination_path

    counter = 1
    while True:
        new_path = destination_path.parent / (destination_path.stem + "_" + str(counter) + destination_path.suffix)
        if not new_path.exists():
            return new_path
        counter = counter + 1


from watchdog.events import FileSystemEventHandler

class DownloadHandler (FileSystemEventHandler):
    def __init__(self, destination_root):
        self.destination_root = destination_root
    
    def on_created(self, event):
        organize_file(event.src_path, self.destination_root)

import time
from watchdog.observers import Observer

if __name__ == "__main__":
    watch_folder ="/Users/borhanrahimi/Desktop/organizer_playground/source"
    destination_root = "/Users/borhanrahimi/Desktop/organizer_playground/organized"

    observer = Observer()
    observer.schedule(DownloadHandler(destination_root), watch_folder, recursive=False)
    observer.start()

    print(f"Watching folder: {watch_folder}...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()