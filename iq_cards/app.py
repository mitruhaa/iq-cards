from __future__ import annotations

import os
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_from_directory, url_for

from . import db
from .importer import CardImportError, clear_all, import_cards


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    root_dir = Path(__file__).resolve().parent.parent
    data_dir = Path(os.environ.get("IQCARDS_DATA_DIR", root_dir / "data"))
    import_dir = Path(os.environ.get("IQCARDS_IMPORT_DIR", root_dir / "import"))

    app.config.from_mapping(
        DATA_DIR=data_dir,
        DATABASE=data_dir / "cards.sqlite3",
        ASSET_DIR=data_dir / "assets",
        IMPORT_DIR=import_dir,
        JSON_SORT_KEYS=False,
    )
    if test_config:
        app.config.update(test_config)

    Path(app.config["DATA_DIR"]).mkdir(parents=True, exist_ok=True)
    Path(app.config["ASSET_DIR"]).mkdir(parents=True, exist_ok=True)
    db.init_app(app)

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok", "cards": db.card_count()})

    @app.get("/api/cards")
    def cards():
        cards_payload = []
        for card in db.list_cards():
            cards_payload.append(
                {
                    "id": card["id"],
                    "question": card["question"],
                    "answer": {
                        "text": card["answer_text"],
                        "images": [
                            {
                                "filename": filename,
                                "url": url_for("asset_file", filename=filename),
                            }
                            for filename in card["answer_images"]
                        ],
                    },
                }
            )
        return jsonify({"cards": cards_payload, "total": len(cards_payload)})

    @app.post("/api/import")
    def import_endpoint():
        payload = request.get_json(silent=True) or {}
        mode = payload.get("mode", "replace")
        try:
            result = import_cards(
                db.get_db(),
                Path(app.config["IMPORT_DIR"]),
                Path(app.config["ASSET_DIR"]),
                mode,
            )
        except CardImportError as exc:
            return jsonify({"error": str(exc)}), 400
        return jsonify(result)

    @app.post("/api/clear")
    def clear_endpoint():
        result = clear_all(db.get_db(), Path(app.config["ASSET_DIR"]))
        return jsonify(result)

    @app.get("/assets/<path:filename>")
    def asset_file(filename: str):
        return send_from_directory(Path(app.config["ASSET_DIR"]), filename)

    return app
