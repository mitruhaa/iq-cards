# IQ Cards

IQ Cards is a small multi-platform flashcards app written in Python. It runs a local web UI in your browser, stores cards in SQLite, imports decks from JSON, supports image answers, and can also run as a Docker container.

The app is intentionally local-first: no account, no external service, and no network access required after dependencies are installed.

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

The browser UI depends on JavaScript for importing, revealing cards, scoring, and navigation. If buttons appear to do nothing, check that JavaScript is enabled for `127.0.0.1`.

## Run On Linux

```bash
./launch_linux.sh
```

The script creates `.venv` if needed, installs `requirements.txt`, starts the app, and opens:

```text
http://127.0.0.1:5000/
```

## Run On Windows

Double-click `launch_windows.bat`, or run:

```bat
launch_windows.bat
```

It creates `.venv`, installs dependencies, and starts the same local browser app.

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

## Development

Install development dependencies:

```bash
python -m pip install -r requirements-dev.txt
```

Run tests:

```bash
python -m pytest
```

Install Playwright's browser runtime for visual UI tests:

```bash
python -m playwright install chromium
python -m pytest tests/test_ui_playwright.py
```

## Troubleshooting

Button clicks do nothing:

- Make sure JavaScript is enabled in the browser.
- Hard refresh the page with `Ctrl+F5` after changing frontend files.
- Open the browser devtools console and check for errors.

Import says an image is missing:

- Confirm the image exists under `import/assets/`.
- Use the same filename in `cards.json`, including extension.
- Do not use absolute paths or `../`.

The app imports from the wrong folder:

- Start it from this project directory, or pass `--import-dir /path/to/import`.
- In Docker, mount your import folder to `/app/import`.

Port already in use:

```bash
python -m iq_cards --port 5010
```

Docker cannot save cards between runs:

- Mount a persistent data volume with `-v "$PWD/data:/app/data"`.
