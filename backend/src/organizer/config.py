from pathlib import Path
import yaml

class ConfigError(Exception):
    """Raised when config.yaml is missing or has invalid settings."""

REQUIRED_KEYS = ("watch_folder", "destination_root", "categories")

# Used by the desktop app before the user has saved any settings.
DEFAULT_CATEGORIES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"],
    "Documents": [".pdf", ".docx", ".txt", ".xlsx"],
    "Videos": [".mp4", ".avi", ".mov"],
    "Music": [".mp3", ".wav", ".flac"],
    "Archives": [".zip", ".rar", ".tar.gz"],
}

def read_config_file(config_path):
    """Return the raw settings in a config file, without validating them."""
    path= Path(config_path)

    try:
        with open(path) as f :
            config = yaml.safe_load(f)
    except FileNotFoundError:
        raise ConfigError(f"Config file not found: {path}")
    except yaml.YAMLError as error:
        raise ConfigError(f"Config file is not valid YAML: {error}")

    if not isinstance(config, dict):
        raise ConfigError("Config file must contain 'key: value' settings")

    return config

def validate_config(config):
    """Check raw settings and return (watch_folder, destination_root, categories)."""
    for key in REQUIRED_KEYS:
        if key not in config:
            raise ConfigError(f"Missing required setting:{key}")

    for key in ("watch_folder", "destination_root"):
        if not isinstance(config[key], str) or not config[key].strip():
            raise ConfigError(f"{key} must be a folder path")

    watch_folder = Path(config ["watch_folder"]).expanduser().resolve()
    destination_root = Path(config["destination_root"]).expanduser().resolve()

    if not watch_folder.is_dir():
        raise ConfigError(f"watch_folder is not an existing folder: {watch_folder}")
    if watch_folder.is_relative_to(destination_root):
        raise ConfigError(
            "watch_folder must not be the same as, or inside, destination_root"
        )

    categories = config["categories"]
    if not isinstance(categories, dict) or not categories:
        raise ConfigError("categories must list at least one category")

    for category, extensions in categories.items():
        # Category names become folder names, so they must not escape the destination.
        if (
            not isinstance(category, str)
            or category in ("", ".", "..")
            or "/" in category
            or "\\" in category
        ):
            raise ConfigError(f"Category name {category!r} must be a plain folder name")
        if not isinstance(extensions, list):
            raise ConfigError(f"Category '{category}' must have a list of extensions")
        for extension in extensions:
            if not isinstance(extension, str) or not extension.startswith("."):
                raise ConfigError(
                    f"Extension {extension!r} in '{category}' must start with a dot, like .pdf"
                )

    # The last line of the function
    return str(watch_folder), str(destination_root), categories

def load_config(config_path):
    return validate_config(read_config_file(config_path))

def save_config(config_path, watch_folder, destination_root, categories):
    path = Path(config_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    settings = {
        "watch_folder": watch_folder,
        "destination_root": destination_root,
        "categories": categories,
    }

    # Write to a temporary file first so a crash never leaves a half-written config.
    temporary = path.with_name(path.name + ".tmp")
    with open(temporary, "w") as f:
        yaml.safe_dump(settings, f, sort_keys=False)
    temporary.replace(path)
