import shutil
from pathlib import Path
import logging


# Matches by the end of the filename so multi-part extensions like ".tar.gz"
# work. The longest matching extension wins, so ".tar.gz" beats ".gz".
def get_category(filename, categories):
    name = Path(filename).name.lower()
    best_category = "Others"
    best_length = 0

    for category, extensions in categories.items():
        for extension in extensions:
            if name.endswith(extension.lower()) and len(extension) > best_length:
                best_category = category
                best_length = len(extension)

    return best_category

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