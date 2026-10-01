import pytest

from organizer.server import main


def test_server_exits_without_token(monkeypatch, capsys):
    monkeypatch.delenv("ORGANIZER_TOKEN", raising=False)

    with pytest.raises(SystemExit) as exit_info:
        main(["--port", "8000"])

    assert exit_info.value.code == 1
    assert "ORGANIZER_TOKEN must be set." in capsys.readouterr().err



def test_server_requires_port(monkeypatch):
    monkeypatch.setenv("ORGANIZER_TOKEN", "test-token")

    with pytest.raises(SystemExit) as exit_info:
        main([])
    assert exit_info.value.code == 2