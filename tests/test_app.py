from pathlib import Path

from .conftest import write_import


SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"></svg>'


def text_card(question="Question?", answer="Answer."):
    return {"question": question, "answer": {"text": answer, "images": []}}


def test_health_and_empty_cards(client):
    health = client.get("/api/health")
    assert health.status_code == 200
    assert health.json == {"status": "ok", "cards": 0}

    cards = client.get("/api/cards")
    assert cards.status_code == 200
    assert cards.json == {"cards": [], "total": 0}


def test_replace_import_overwrites_existing_deck(app, client):
    write_import(
        app,
        [
            text_card("First?", "One."),
            {
                "question": "Shape?",
                "answer": {"text": "Triangle.", "images": ["triangle.svg"]},
            },
        ],
        {"triangle.svg": SVG},
    )
    response = client.post("/api/import", json={"mode": "replace"})
    assert response.status_code == 200
    assert response.json["imported"] == 2
    assert response.json["total"] == 2

    write_import(app, [text_card("Replacement?", "Only card.")])
    response = client.post("/api/import", json={"mode": "replace"})
    assert response.status_code == 200
    assert response.json["imported"] == 1
    assert response.json["total"] == 1

    cards = client.get("/api/cards").json["cards"]
    assert [card["question"] for card in cards] == ["Replacement?"]


def test_append_import_keeps_existing_deck(app, client):
    write_import(app, [text_card("First?", "One.")])
    assert client.post("/api/import", json={"mode": "replace"}).json["total"] == 1

    write_import(app, [text_card("Second?", "Two.")])
    response = client.post("/api/import", json={"mode": "append"})
    assert response.status_code == 200
    assert response.json["total"] == 2

    cards = client.get("/api/cards").json["cards"]
    assert [card["question"] for card in cards] == ["First?", "Second?"]


def test_clear_removes_cards_and_copied_assets(app, client):
    write_import(
        app,
        [
            {
                "question": "Shape?",
                "answer": {"text": "Triangle.", "images": ["triangle.svg"]},
            }
        ],
        {"triangle.svg": SVG},
    )
    assert client.post("/api/import", json={"mode": "replace"}).status_code == 200
    assert list(Path(app.config["ASSET_DIR"]).iterdir())

    response = client.post("/api/clear", json={})
    assert response.status_code == 200
    assert response.json == {"total": 0}
    assert client.get("/api/cards").json == {"cards": [], "total": 0}
    assert list(Path(app.config["ASSET_DIR"]).iterdir()) == []


def test_import_rejects_missing_asset_without_mutating_existing_deck(app, client):
    write_import(app, [text_card("Existing?", "Still here.")])
    assert client.post("/api/import", json={"mode": "replace"}).json["total"] == 1

    write_import(
        app,
        [
            {
                "question": "Broken?",
                "answer": {"text": "No image.", "images": ["missing.svg"]},
            }
        ],
    )
    response = client.post("/api/import", json={"mode": "replace"})
    assert response.status_code == 400
    assert "was not found" in response.json["error"]

    cards = client.get("/api/cards").json["cards"]
    assert [card["question"] for card in cards] == ["Existing?"]


def test_import_rejects_path_traversal(app, client):
    write_import(
        app,
        [
            {
                "question": "Unsafe?",
                "answer": {"text": "No.", "images": ["../secret.svg"]},
            }
        ],
    )
    response = client.post("/api/import", json={"mode": "replace"})
    assert response.status_code == 400
    assert "inside import/assets" in response.json["error"]


def test_import_rejects_unsupported_image_extension(app, client):
    write_import(
        app,
        [
            {
                "question": "Unsafe extension?",
                "answer": {"text": "No.", "images": ["notes.txt"]},
            }
        ],
        {"notes.txt": "not an image"},
    )
    response = client.post("/api/import", json={"mode": "replace"})
    assert response.status_code == 400
    assert "unsupported extension" in response.json["error"]


def test_import_rejects_card_without_answer_content(app, client):
    write_import(app, [{"question": "Empty answer?", "answer": {"text": "", "images": []}}])
    response = client.post("/api/import", json={"mode": "replace"})
    assert response.status_code == 400
    assert "answer text, images, or both" in response.json["error"]
