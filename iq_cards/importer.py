from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path, PurePosixPath

from werkzeug.utils import secure_filename

from . import db as card_db


ALLOWED_IMAGE_EXTENSIONS = {".gif", ".jpeg", ".jpg", ".png", ".svg", ".webp"}


class CardImportError(ValueError):
    pass


def import_cards(connection, import_dir: Path, asset_dir: Path, mode: str) -> dict:
    if mode not in {"replace", "append"}:
        raise CardImportError("Import mode must be 'replace' or 'append'.")

    import_dir = Path(import_dir)
    asset_dir = Path(asset_dir)
    cards_file = import_dir / "cards.json"
    source_assets_dir = import_dir / "assets"

    parsed_cards = _load_cards(cards_file, source_assets_dir)
    asset_dir.mkdir(parents=True, exist_ok=True)
    copied_cards = _copy_card_assets(parsed_cards, asset_dir)

    try:
        if mode == "replace":
            connection.execute("DELETE FROM cards")
        card_db.insert_cards(connection, copied_cards)
        connection.commit()
    except Exception:
        connection.rollback()
        raise

    prune_unreferenced_assets(connection, asset_dir)

    return {
        "imported": len(copied_cards),
        "mode": mode,
        "total": card_db.card_count(connection),
    }


def clear_all(connection, asset_dir: Path) -> dict:
    connection.execute("DELETE FROM cards")
    connection.commit()
    prune_unreferenced_assets(connection, asset_dir)
    return {"total": 0}


def prune_unreferenced_assets(connection, asset_dir: Path) -> None:
    asset_dir = Path(asset_dir)
    if not asset_dir.exists():
        return

    referenced = set()
    for card in card_db.list_cards(connection):
        referenced.update(card["answer_images"])

    for path in asset_dir.iterdir():
        if path.is_file() and path.name not in referenced:
            path.unlink()


def _load_cards(cards_file: Path, source_assets_dir: Path) -> list[dict]:
    if not cards_file.exists():
        raise CardImportError(f"Missing import file: {cards_file}")

    try:
        payload = json.loads(cards_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CardImportError(f"Invalid JSON in cards.json: {exc.msg}") from exc

    if not isinstance(payload, dict) or not isinstance(payload.get("cards"), list):
        raise CardImportError("cards.json must contain an object with a 'cards' array.")

    cards = []
    for index, raw_card in enumerate(payload["cards"], start=1):
        cards.append(_parse_card(index, raw_card, source_assets_dir))

    if not cards:
        raise CardImportError("cards.json must contain at least one card.")

    return cards


def _parse_card(index: int, raw_card: object, source_assets_dir: Path) -> dict:
    if not isinstance(raw_card, dict):
        raise CardImportError(f"Card {index} must be an object.")

    question = raw_card.get("question")
    if not isinstance(question, str) or not question.strip():
        raise CardImportError(f"Card {index} must have a non-empty question.")

    answer = raw_card.get("answer")
    if not isinstance(answer, dict):
        raise CardImportError(f"Card {index} must have an answer object.")

    answer_text = answer.get("text")
    if answer_text is not None and not isinstance(answer_text, str):
        raise CardImportError(f"Card {index} answer.text must be text.")
    answer_text = answer_text.strip() if isinstance(answer_text, str) else None
    if answer_text == "":
        answer_text = None

    image_refs = answer.get("images", [])
    if image_refs is None:
        image_refs = []
    if not isinstance(image_refs, list):
        raise CardImportError(f"Card {index} answer.images must be an array.")

    images = [
        _validate_asset_reference(index, image_ref, source_assets_dir)
        for image_ref in image_refs
    ]

    if answer_text is None and not images:
        raise CardImportError(f"Card {index} must have answer text, images, or both.")

    return {
        "question": question.strip(),
        "answer_text": answer_text,
        "source_images": images,
    }


def _validate_asset_reference(
    card_index: int,
    image_ref: object,
    source_assets_dir: Path,
) -> Path:
    if not isinstance(image_ref, str) or not image_ref.strip():
        raise CardImportError(f"Card {card_index} image references must be text.")
    if "\\" in image_ref or ":" in image_ref:
        raise CardImportError(
            f"Card {card_index} image '{image_ref}' must be a relative asset path."
        )

    normalized = image_ref.strip()
    pure_path = PurePosixPath(normalized)
    if pure_path.is_absolute() or any(part in {"", ".", ".."} for part in pure_path.parts):
        raise CardImportError(
            f"Card {card_index} image '{image_ref}' must stay inside import/assets."
        )
    if pure_path.suffix.lower() not in ALLOWED_IMAGE_EXTENSIONS:
        raise CardImportError(
            f"Card {card_index} image '{image_ref}' has an unsupported extension."
        )

    source_path = (source_assets_dir / Path(*pure_path.parts)).resolve()
    assets_root = source_assets_dir.resolve()
    if not source_path.is_relative_to(assets_root):
        raise CardImportError(
            f"Card {card_index} image '{image_ref}' must stay inside import/assets."
        )
    if not source_path.is_file():
        raise CardImportError(f"Card {card_index} image '{image_ref}' was not found.")

    return source_path


def _copy_card_assets(cards: list[dict], asset_dir: Path) -> list[dict]:
    copied_by_source = {}
    copied_cards = []

    for card in cards:
        copied_images = []
        for source_image in card["source_images"]:
            copied_name = copied_by_source.get(source_image)
            if copied_name is None:
                copied_name = _copy_asset(source_image, asset_dir)
                copied_by_source[source_image] = copied_name
            copied_images.append(copied_name)

        copied_cards.append(
            {
                "question": card["question"],
                "answer_text": card["answer_text"],
                "answer_images": copied_images,
            }
        )

    return copied_cards


def _copy_asset(source_image: Path, asset_dir: Path) -> str:
    content = source_image.read_bytes()
    digest = hashlib.sha256(content).hexdigest()[:12]
    safe_name = secure_filename(source_image.name)
    if not safe_name:
        safe_name = f"asset{source_image.suffix.lower()}"
    target_name = f"{digest}-{safe_name}"
    target_path = asset_dir / target_name
    if not target_path.exists():
        shutil.copy2(source_image, target_path)
    return target_name
