import logging
import sys

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

    start_watching(watch_folder, destination_root, categories)

if __name__ == "__main__":
    main()
