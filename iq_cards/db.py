import json
import sqlite3
from pathlib import Path

from flask import current_app, g


SCHEMA = """
CREATE TABLE IF NOT EXISTS cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    answer_text TEXT,
    answer_images TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


def get_db() -> sqlite3.Connection:
    db = g.get("db")
    if db is None:
        database = Path(current_app.config["DATABASE"])
        database.parent.mkdir(parents=True, exist_ok=True)
        db = sqlite3.connect(database)
        db.row_factory = sqlite3.Row
        g.db = db
    return db


def close_db(_exception=None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db() -> None:
    db = get_db()
    db.executescript(SCHEMA)
    db.commit()


def init_app(app) -> None:
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()


def card_count(db: sqlite3.Connection | None = None) -> int:
    db = db or get_db()
    row = db.execute("SELECT COUNT(*) AS count FROM cards").fetchone()
    return int(row["count"])


def list_cards(db: sqlite3.Connection | None = None) -> list[dict]:
    db = db or get_db()
    rows = db.execute(
        """
        SELECT id, question, answer_text, answer_images
        FROM cards
        ORDER BY id ASC
        """
    ).fetchall()
    return [
        {
            "id": row["id"],
            "question": row["question"],
            "answer_text": row["answer_text"],
            "answer_images": json.loads(row["answer_images"]),
        }
        for row in rows
    ]


def insert_cards(db: sqlite3.Connection, cards: list[dict]) -> None:
    db.executemany(
        """
        INSERT INTO cards (question, answer_text, answer_images)
        VALUES (?, ?, ?)
        """,
        [
            (
                card["question"],
                card.get("answer_text"),
                json.dumps(card.get("answer_images", [])),
            )
            for card in cards
        ],
    )


def clear_cards(db: sqlite3.Connection | None = None) -> None:
    db = db or get_db()
    db.execute("DELETE FROM cards")
    db.commit()
