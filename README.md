# IQ Cards

IQ Cards is a small multi-platform flashcards app written in Python. It runs a local web UI in your browser, stores cards in SQLite, imports decks from JSON, supports image answers, and can also run as a Docker container.


## Features

- Question-first flashcards with a flip animation for reveal.
- Answers can contain text, images, or both.
- Correct and incorrect answers are counted during each study session.
- End-of-session summary shows correct count, total cards, and percentage.
- `Import cards` replaces the current deck.
- `Add cards` appends imported cards to the current deck.
- `Clear all cards` removes the stored deck and copied assets.
- Sample deck included in `import/cards.json`.
- Linux, Windows, and Docker launch paths.

## Requirements

- Python 3.11 or newer is recommended.
- A modern browser with JavaScript enabled.
- Docker is optional.

## Run On Linux

```bash
./launch_linux.sh
```
Address:
```text
http://127.0.0.1:5000/
```

## Run On Windows

Double-click `launch_windows.bat`, or run:

```bat
launch_windows.bat
```
Launches the app on the same address

## Manual Run

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python -m iq_cards
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m iq_cards
```

Useful options:

```bash
python -m iq_cards --host 127.0.0.1 --port 5000
python -m iq_cards --no-browser
python -m iq_cards --data-dir ./data --import-dir ./import
```

Environment overrides:

- `IQCARDS_DATA_DIR`: runtime database and copied assets directory.
- `IQCARDS_IMPORT_DIR`: folder containing `cards.json` and `assets/`.
- `IQCARDS_HOST`: server host, default `127.0.0.1`.
- `IQCARDS_PORT`: server port, default `5000`.
- `IQCARDS_OPEN_BROWSER`: set to `0` to prevent automatic browser opening.

## Docker

Build:

```bash
docker build -t iq-cards .
```

Run:

```bash
docker run --rm -p 8000:8000 iq-cards
```

Open:

```text
http://127.0.0.1:8000/
```

To keep the database between container runs, mount a data directory:

```bash
docker run --rm -p 8000:8000 -v "$PWD/data:/app/data" iq-cards
```

To provide your own import folder:

```bash
docker run --rm -p 8000:8000 \
  -v "$PWD/import:/app/import:ro" \
  -v "$PWD/data:/app/data" \
  iq-cards
```

## Importing Cards

The app imports from:

```text
import/cards.json
import/assets/
```

`Import cards` replaces the current deck. `Add cards` appends the cards from the same import folder.

Basic format:

```json
{
  "cards": [
    {
      "question": "What is the capital of Italy?",
      "answer": {
        "text": "Rome",
        "images": []
      }
    },
    {
      "question": "What does an equilateral triangle look like?",
      "answer": {
        "text": "It has three equal sides and three equal angles.",
        "images": ["triangle.svg"]
      }
    }
  ]
}
```

Rules:

- `question` must be non-empty text.
- `answer.text` is optional.
- `answer.images` is optional and must be a list of image filenames.
- Each card must have answer text, images, or both.
- Image paths are relative to `import/assets/`.
- Absolute paths and `..` path traversal are rejected.
- Supported image extensions: `png`, `jpg`, `jpeg`, `gif`, `webp`, `svg`.

Images are copied into `data/assets/` with safe hash-prefixed filenames. The original `import/assets/` files are not modified.

## Data Storage

Runtime data lives in `data/` by default:

```text
data/cards.sqlite3
data/assets/
```

`data/` is ignored by Git so local decks do not get committed accidentally.
