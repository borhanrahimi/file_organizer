import pytest

from organizer.config import ConfigError, load_config


def write_config(tmp_path, text):
    config_file = tmp_path / "config.yaml"
    config_file.write_text(text)
    return config_file


def test_missing_file_raises_config_error(tmp_path):
    with pytest.raises(ConfigError, match="not found"):
        load_config(tmp_path / "does_not_exist.yaml")


def test_empty_file_raises_config_error(tmp_path):
    config_file = write_config(tmp_path, "")

    with pytest.raises(ConfigError):
        load_config(config_file)


def test_missing_categories_raises_config_error(tmp_path):
    watch = tmp_path / "watch"
    watch.mkdir()
    config_file = write_config(tmp_path, f"""
watch_folder: "{watch}"
destination_root: "{tmp_path / 'organized'}"
""")

    with pytest.raises(ConfigError, match="categories"):
        load_config(config_file)


def test_watch_folder_that_does_not_exist_raises_config_error(tmp_path):
    config_file = write_config(tmp_path, f"""
watch_folder: "{tmp_path / 'not_here'}"
destination_root: "{tmp_path / 'organized'}"
categories:
  Images: [.jpg]
""")

    with pytest.raises(ConfigError, match="not an existing folder"):
        load_config(config_file)


def test_same_watch_and_destination_raises_config_error(tmp_path):
    watch = tmp_path / "watch"
    watch.mkdir()
    config_file = write_config(tmp_path, f"""
watch_folder: "{watch}"
destination_root: "{watch}"
categories:
  Images: [.jpg]
""")

    with pytest.raises(ConfigError, match="inside"):
        load_config(config_file)


def test_extension_without_dot_raises_config_error(tmp_path):
    watch = tmp_path / "watch"
    watch.mkdir()
    config_file = write_config(tmp_path, f"""
watch_folder: "{watch}"
destination_root: "{tmp_path / 'organized'}"
categories:
  Images: [jpg]
""")

    with pytest.raises(ConfigError, match="must start with a dot"):
        load_config(config_file)


def test_valid_config_returns_settings(tmp_path):
    watch = tmp_path / "watch"
    watch.mkdir()
    destination = watch / "organized"
    config_file = write_config(tmp_path, f"""
watch_folder: "{watch}"
destination_root: "{destination}"
categories:
  Images: [.jpg, .png]
""")

    watch_folder, destination_root, categories = load_config(config_file)

    assert watch_folder == str(watch.resolve())
    assert destination_root == str(destination.resolve())
    assert categories == {"Images": [".jpg", ".png"]}
