import argparse
import logging
import os 
import sys
import threading
import time

import uvicorn
from organizer.api import create_app
from organizer.lock import default_data_folder, default_lock_path
from organizer.service import OrganizerService

TOKEN_VARIABLE = "ORGANIZER_TOKEN"


def process_exists(pid):
    try:
        os.kill(pid, 0)  # Signal 0 only checks that the process exists.
    except ProcessLookupError:
        return False
    except PermissionError:
        return True  # It exists but belongs to another user.
    return True


def exit_when_parent_exits(parent_pid, request_exit, check_seconds=1.0):
    """Call request_exit once the app process (parent_pid) has gone.

    Covers the app crashing or being killed before it can send /shutdown.
    This checks the app's process id rather than this process's parent,
    because the packaged backend runs under a small launcher process.
    """
    if sys.platform == "win32":
        # os.kill() would end the process on Windows; the app's own
        # shutdown handles Windows instead.
        return

    def watch():
        while process_exists(parent_pid):
            time.sleep(check_seconds)
        request_exit()

    threading.Thread(target=watch, name="parent-watch", daemon=True).start()


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run the file organizer API server.")
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument(
        "--settings",
        default=str(default_data_folder() / "settings.yaml"),
        help="Settings file to read and save (default: the user's app data folder).",
    )
    parser.add_argument(
        "--lock-file",
        default=str(default_lock_path()),
        help="Lock file shared by every organizer on this computer.",
    )
    parser.add_argument(
        "--parent-pid",
        type=int,
        help="Shut down when this process (the app that started the server) exits.",
    )
    args = parser.parse_args(argv)

    token = os.environ.get(TOKEN_VARIABLE)
    if not token:
        print(f"{TOKEN_VARIABLE} must be set.", file=sys.stderr)
        sys.exit(1)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    service = OrganizerService(args.settings, args.lock_file)
    server = None

    def request_exit():
        server.should_exit = True

    app = create_app(token, service, on_shutdown=request_exit)
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=args.port))
    if args.parent_pid is not None:
        exit_when_parent_exits(args.parent_pid, request_exit)

    try:
        server.run()
    finally:
        # Ctrl+C or a signal from the app also stops the watcher cleanly.
        service.stop()


if __name__ == "__main__":
    main()
