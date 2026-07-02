# IQ Cards Implementation Plan

## Summary
Build a Python flashcards app as a local browser UI served by Flask and Waitress. It runs on Linux and Windows through simple launch scripts and in Docker on port 8000. Cards persist in SQLite, answer images are copied from `import/assets`, and the UI provides a minimal animated card-flip study flow.

`Import cards` replaces the existing deck. `Add cards` appends to it.

## Interfaces
- Import file: `import/cards.json`
- Assets: `import/assets/`
- Runtime data: `data/cards.sqlite3` and `data/assets/`
- Entrypoint: `python -m iq_cards`
- Environment overrides: `IQCARDS_DATA_DIR`, `IQCARDS_IMPORT_DIR`, `IQCARDS_HOST`, `IQCARDS_PORT`, `IQCARDS_OPEN_BROWSER`

Example card schema:

```json
{
  "cards": [
    {
      "question": "What is 2 + 2?",
      "answer": {
        "text": "4",
        "images": []
      }
    }
  ]
}
```

## Implementation
- Flask serves the app shell, JSON API, health endpoint, and imported assets.
- SQLite stores each card with question, optional answer text, and a JSON array of copied image filenames.
- The importer validates every card before database mutation, rejects unsafe asset paths, supports common image extensions, and prunes unreferenced copied assets.
- The browser UI loads all cards once, tracks session score client-side, flips the card on reveal, and shows the final correct/total/percent summary.
- Docker uses `python:3.13-slim` and runs Waitress with browser opening disabled.

## Test Plan
- Pytest covers health, card listing, replace import, append import, clear-all behavior, missing assets, bad extensions, path traversal, and malformed card data.
- Optional Playwright coverage launches the app in a live test server, imports sample cards, checks the flip flow, marks answers, reaches the summary, and saves screenshots to the test temp directory.
- Smoke checks include local server health and Docker build/run when Docker is available.
