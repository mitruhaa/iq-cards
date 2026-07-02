from pathlib import Path

import pytest

from iq_cards import create_app


@pytest.fixture()
def app(tmp_path):
    import_dir = tmp_path / "import"
    data_dir = tmp_path / "data"
    (import_dir / "assets").mkdir(parents=True)

    app = create_app(
        {
            "TESTING": True,
            "DATA_DIR": data_dir,
            "DATABASE": data_dir / "cards.sqlite3",
            "ASSET_DIR": data_dir / "assets",
            "IMPORT_DIR": import_dir,
        }
    )
    return app


@pytest.fixture()
def client(app):
    return app.test_client()


def write_import(app, cards, assets=None):
    import_dir = Path(app.config["IMPORT_DIR"])
    assets_dir = import_dir / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)

    import json

    (import_dir / "cards.json").write_text(
        json.dumps({"cards": cards}, indent=2),
        encoding="utf-8",
    )

    for name, content in (assets or {}).items():
        path = assets_dir / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
