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
    pass