import shutil
from pathlib import Path
import logging


# TODO: Path().suffix only grabs the last extension, so "file.tar.gz" becomes
# ".gz" not ".tar.gz" and won't match the Archives category correctly.
def get_category(filename, categories):
    extension = Path(filename).suffix.lower()
    for category, extensions in categories.items():
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


def organize_file(filepath, destination_root, categories):
    filename = Path(filepath).name
    category = get_category(filename, categories)
    new_name = clean_filename(filename)
    destination_path = Path(destination_root) / category / new_name
    destination_path = unique_path(destination_path)

    destination_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(filepath, destination_path)
    logging.info("Moved file: %s -> %s", filepath, destination_path)

def unique_path(destination_path):
    if not destination_path.exists():
        return destination_path

    counter = 1
    while True:
        new_path = destination_path.parent / (destination_path.stem + "_" + str(counter) + destination_path.suffix)
        if not new_path.exists():
            return new_path
        counter = counter + 1