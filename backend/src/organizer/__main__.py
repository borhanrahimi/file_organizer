import logging
import sys

from organizer import lock
from organizer.config import ConfigError, load_config
from organizer.watcher import start_watching

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    try:
        watch_folder, destination_root, categories = load_config("config.yaml")
    except ConfigError as error:
        print(f"Config error: {error}", file=sys.stderr)
        sys.exit(1)

    # The same lock the desktop app takes, so the two never watch at once.
    organizer_lock = lock.OrganizerLock(lock.default_lock_path())
    try:
        organizer_lock.acquire()
    except lock.LockHeldError as error:
        print(error, file=sys.stderr)
        sys.exit(1)

    try:
        start_watching(watch_folder, destination_root, categories)
    finally:
        organizer_lock.release()

if __name__ == "__main__":
    main()
