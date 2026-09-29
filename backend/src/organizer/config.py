from pathlib import Path 
import yaml

class ConfigError(Exception):
    """Raised when config.yaml is missing or has invalid settings."""

REQUIRED_KEYS = ("watch_folder", "destination_root", "categories")

def load_config(config_path):
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
    
    for key in REQUIRED_KEYS:
        if key not in config:
            raise ConfigError(f"Missing required setting:{key}")
        
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
        if not isinstance(extensions, list):
            raise ConfigError(f"Category '{category}' must have a list of extensions")
        for extension in extensions:
            if not isinstance(extension, str) or not extension.startswith("."):
                raise ConfigError(
                    f"Extension {extension!r} in '{category}' must start with a dot, like .pdf"
                )

    # The last line of the function
    return str(watch_folder), str(destination_root), categories