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

def test_shutdown_request_ends_the_server_process(tmp_path):
    import json
    import os
    import socket
    import subprocess
    import sys
    import time
    import urllib.request

    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]

    process = subprocess.Popen(
        [
            sys.executable, "-m", "organizer.server",
            "--port", str(port),
            "--settings", str(tmp_path / "settings.yaml"),
            "--lock-file", str(tmp_path / "organizer.lock"),
        ],
        env={**os.environ, "ORGANIZER_TOKEN": "test-token"},
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    def call(method, path):
        request = urllib.request.Request(
            f"http://127.0.0.1:{port}{path}",
            method=method,
            headers={"Authorization": "Bearer test-token"},
        )
        with urllib.request.urlopen(request, timeout=2) as response:
            return json.load(response)

    try:
        deadline = time.monotonic() + 10
        while True:
            try:
                status = call("GET", "/status")
                break
            except OSError:
                assert process.poll() is None, process.stderr.read().decode()
                assert time.monotonic() < deadline, "server did not start"
                time.sleep(0.1)

        assert status == {"state": "stopped", "message": None}
        assert call("POST", "/shutdown") == {"state": "stopped", "message": None}
        assert process.wait(timeout=5) == 0
    finally:
        if process.poll() is None:
            process.kill()
        process.communicate()


def test_server_exits_when_its_parent_process_exits(tmp_path):
    import os
    import socket
    import subprocess
    import sys
    import time

    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]

    pid_file = tmp_path / "server.pid"
    # A short-lived parent starts the server, records its process id, and exits.
    parent_script = f"""
import os, subprocess, sys
child = subprocess.Popen([
    sys.executable, "-m", "organizer.server", "--port", "{port}",
    "--settings", r"{tmp_path / 'settings.yaml'}",
    "--lock-file", r"{tmp_path / 'organizer.lock'}",
    "--parent-pid", str(os.getpid()),
], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
open(r"{pid_file}", "w").write(str(child.pid))
"""
    env = {**os.environ, "ORGANIZER_TOKEN": "test-token"}
    subprocess.run([sys.executable, "-c", parent_script], env=env, check=True)
    server_pid = int(pid_file.read_text())

    def is_running(pid):
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return False
        return True

    try:
        deadline = time.monotonic() + 10
        while is_running(server_pid) and time.monotonic() < deadline:
            time.sleep(0.2)
        assert not is_running(server_pid)
    finally:
        if is_running(server_pid):
            os.kill(server_pid, 9)
