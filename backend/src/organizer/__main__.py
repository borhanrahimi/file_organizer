import logging

import yaml

from organizer.watcher import start_watching

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )
    with open("config.yaml") as f:
        config = yaml.safe_load(f)

    watch_folder = config["watch_folder"]
    destination_root = config["destination_root"]
    categories = config["categories"]

    start_watching(watch_folder, destination_root, categories)

if __name__ == "__main__":
    main()