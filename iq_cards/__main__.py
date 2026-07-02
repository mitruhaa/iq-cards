from __future__ import annotations

import argparse
import os
import threading
import webbrowser
from pathlib import Path

from waitress import serve

from .app import create_app


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the IQ Cards flashcards app.")
    parser.add_argument("--host", default=os.environ.get("IQCARDS_HOST", "127.0.0.1"))
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("IQCARDS_PORT", "5000")),
    )
    parser.add_argument("--data-dir", default=os.environ.get("IQCARDS_DATA_DIR"))
    parser.add_argument("--import-dir", default=os.environ.get("IQCARDS_IMPORT_DIR"))
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()

    config = {}
    if args.data_dir:
        data_dir = Path(args.data_dir)
        config.update(
            DATA_DIR=data_dir,
            DATABASE=data_dir / "cards.sqlite3",
            ASSET_DIR=data_dir / "assets",
        )
    if args.import_dir:
        config["IMPORT_DIR"] = Path(args.import_dir)

    app = create_app(config)
    display_host = "127.0.0.1" if args.host == "0.0.0.0" else args.host
    url = f"http://{display_host}:{args.port}/"

    if not args.no_browser and os.environ.get("IQCARDS_OPEN_BROWSER", "1") != "0":
        threading.Timer(0.8, lambda: webbrowser.open_new_tab(url)).start()

    print(f"IQ Cards is running at {url}")
    serve(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
