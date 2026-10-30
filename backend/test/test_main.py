import pytest

from organizer import lock
from organizer.__main__ import main


def test_terminal_mode_exits_when_another_organizer_holds_the_lock(
    tmp_path, monkeypatch, capsys
):
    watch = tmp_path / "downloads"
    watch.mkdir()
    (tmp_path / "config.yaml").write_text(f"""
watch_folder: "{watch}"
destination_root: "{tmp_path / 'organized'}"
categories:
  Images: [.jpg]
""")
    lock_path = tmp_path / "organizer.lock"
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(lock, "default_lock_path", lambda: lock_path)

    other = lock.OrganizerLock(lock_path)
    other.acquire()
    try:
        with pytest.raises(SystemExit) as exit_info:
            main()
    finally:
        other.release()

    assert exit_info.value.code == 1
    assert "Another file organizer is already running" in capsys.readouterr().err
