"""Try the organizer on sample files, without any setup.

    python3 -m organizer.demo [folder]

Creates messy sample downloads in a new folder (a temporary one by default),
runs them through the same scan, readiness, and move steps as the real
organizer, and prints the folder before and after. Real files are never touched.
"""
import argparse
import sys
import tempfile
from pathlib import Path

from organizer.config import DEFAULT_CATEGORIES
from organizer.readiness import FileReadinessTracker
from organizer.watcher import DownloadHandler, queue_existing_files

SAMPLE_FILES = [
    "final_report FINAL (2).docx",
    "IMG 2041.PNG",
    "Vacation Video.mov",
    "song (live).mp3",
    "backup.tar.gz",
    "invoice.pdf",
    "old downloads/invoice.pdf",
    "notes.xyz",
    "Movie.mp4.crdownload",
]


def print_tree(folder, indent="  "):
    for path in sorted(folder.rglob("*")):
        depth = len(path.relative_to(folder).parts) - 1
        name = path.name + ("/" if path.is_dir() else "")
        print(f"{indent}{'  ' * depth}{name}")


def run_demo(folder):
    folder = Path(folder)
    downloads = folder / "Downloads"
    organized = folder / "Organized"

    for name in SAMPLE_FILES:
        path = downloads / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"sample content of {path.name}")

    # Sample files are complete, so there is no need to wait three seconds.
    handler = DownloadHandler(
        organized,
        DEFAULT_CATEGORIES,
        readiness=FileReadinessTracker(stable_seconds=0),
    )
    queue_existing_files(downloads, handler)
    # The first pass records each file's signature; the second finds it unchanged.
    handler.process_pending()
    handler.process_pending()


def main(argv=None):
    parser = argparse.ArgumentParser(description="Try the file organizer on sample files.")
    parser.add_argument(
        "folder",
        nargs="?",
        help="Empty or new folder to use (default: a new temporary folder).",
    )
    args = parser.parse_args(argv)

    if args.folder is None:
        folder = Path(tempfile.mkdtemp(prefix="file-organizer-demo-"))
    else:
        folder = Path(args.folder).expanduser()
        if folder.exists() and any(folder.iterdir()):
            print(f"{folder} is not empty. Choose a new or empty folder.", file=sys.stderr)
            sys.exit(1)
        folder.mkdir(parents=True, exist_ok=True)

    print(f"Demo folder: {folder}\n")
    print("Before:")
    print("  Downloads/")
    for name in SAMPLE_FILES:
        print(f"    {name}")

    run_demo(folder)

    print("\nAfter:")
    print_tree(folder)
    print(
        "\nNames were cleaned, files were sorted by type, the second invoice.pdf"
        "\nwas renamed instead of overwritten, and the unfinished download"
        "\n(.crdownload) was left alone."
    )


if __name__ == "__main__":
    main()
