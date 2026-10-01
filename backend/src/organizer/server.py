import argparse
import os 
import sys

import uvicorn
from organizer.api import create_app

TOKEN_VARIABLE = "ORGANIZER_TOKEN"


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run the file organizer API server.")
    parser.add_argument("--port", type=int, required=True)
    args = parser.parse_args(argv)

    token = os.environ.get(TOKEN_VARIABLE)
    if not token:
        print(f"{TOKEN_VARIABLE} must be set.", file=sys.stderr)
        sys.exit(1)

    uvicorn.run(create_app(token), host="127.0.0.1", port=args.port)


if __name__ == "__main__":
    main()