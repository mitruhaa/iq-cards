# AI Agent Deck Packaging Guide

Use this guide when creating an IQ Cards import deck from any source material. This file is intentionally general: the user will define the preferred question style, answer style, difficulty, tone, granularity, and any domain-specific rules.

Your job is to turn the user’s source material and instructions into a valid import package:

```text
import/
  cards.json
  assets/
    optional-image-files
```

## Core Rule

Follow the user’s requested card format first, as long as the final deck still fits the IQ Cards import schema.

The app only requires this structural shape:

```json
{
  "cards": [
    {
      "question": "Content shown first.",
      "answer": {
        "text": "Content shown after reveal.",
        "images": ["optional-image.png"]
      }
    }
  ]
}
```

The meaning, wording, length, style, and pedagogical format of `question` and `answer.text` are controlled by the user’s instructions.

## Required JSON Constraints

- `cards` must be a non-empty array.
- Each card must have a non-empty `question` string.
- Each card must have an `answer` object.
- Each answer must contain at least one of:
  - non-empty `text`
  - one or more image references in `images`
- `answer.images` may be omitted or set to `[]` when no images are needed.
- `cards.json` must be valid UTF-8 JSON.
- Do not put Markdown fences, comments, trailing commas, or explanatory prose inside `cards.json`.

## Source Handling

Use only the supplied or explicitly allowed source material. Do not invent facts to fill space.

When creating cards:

- Preserve the user’s requested structure and style.
- Cover the source according to the user’s priorities.
- Keep each card useful as a standalone flashcard unless the user asks for a different format.
- Avoid accidental duplicates.
- Keep terminology, names, numbers, labels, and units faithful to the source.
- If the source is ambiguous, prefer conservative wording or omit the uncertain claim.

## Requested Card Counts

If the user asks for a specific number of cards:

- Produce exactly that number when the source supports it.
- If there is too little source material, create as many grounded cards as possible and report the shortfall outside `cards.json`.
- Do not pad with repeated, vague, unsupported, or trivial cards.
- For large decks, distribute cards across the full source instead of exhausting one section first.
- For small decks, prioritize the highest-value material according to the user’s stated goal.

If the user asks for “all possible,” “comprehensive,” or similar:

- Create all useful non-duplicate cards supported by the source.
- Split dense concepts only when that improves usefulness.
- Avoid creating separate cards for details that are not meaningful to remember.

## Image Routing

Place image files here:

```text
import/assets/
```

Reference images from `cards.json` relative to `import/assets/`.

Valid:

```json
"images": ["diagram.png"]
```

Valid with a subfolder:

```json
"images": ["biology/cell-diagram.png"]
```

Invalid:

```json
"images": ["import/assets/diagram.png"]
```

Invalid:

```json
"images": ["/absolute/path/diagram.png"]
```

Invalid:

```json
"images": ["../diagram.png"]
```

Supported extensions:

```text
png, jpg, jpeg, gif, webp, svg
```

## Image Filename Rules

Use filenames that are safe and easy to inspect:

- Lowercase letters, numbers, hyphens, and underscores are preferred.
- Include the correct file extension.
- Avoid spaces and special characters.
- Do not use absolute paths.
- Do not use `..`.
- Do not include `import/assets/` in the JSON image reference.

Good:

```text
cell-diagram.png
chapter-03-map.webp
triangle.svg
```

Avoid:

```text
Image 1 (final).png
../../secret.png
C:\Users\name\image.png
```

If multiple cards use the same visual, save one file and reference it from each card.

## When To Include Images

Use images when the user asks for them or when visuals are necessary to represent the source accurately.

Common cases:

- Diagrams
- Maps
- Charts
- Screenshots
- Geometry
- Anatomy
- Visual identification
- Process flows
- Symbols or notation

Do not add decorative images unless the user specifically wants them.

## Generated Or Recreated Images

If images need to be created:

- Keep them factual and simple.
- Save them under `import/assets/`.
- Reference their filenames in `answer.images`.
- Prefer SVG for simple diagrams when practical.
- Do not recreate copyrighted source images unless the user has rights or the result is sufficiently original and appropriate.

## Minimal Example

```json
{
  "cards": [
    {
      "question": "User-defined front content.",
      "answer": {
        "text": "User-defined back content.",
        "images": []
      }
    },
    {
      "question": "User-defined front content that uses a visual answer.",
      "answer": {
        "text": "Optional user-defined back text.",
        "images": ["example-diagram.svg"]
      }
    }
  ]
}
```

Expected files:

```text
import/
  cards.json
  assets/
    example-diagram.svg
```

## Final Validation Checklist

Before finishing:

- `import/cards.json` exists.
- `cards.json` parses as valid JSON.
- The root object has a non-empty `cards` array.
- The deck follows the user’s requested question and answer format.
- The deck has the requested number of cards when the source supports it.
- Every card has a non-empty `question`.
- Every card has answer text, answer images, or both.
- Every referenced image exists under `import/assets/`.
- No image path starts with `/`, contains `..`, contains backslashes, or includes `import/assets/`.
- No unsupported image extensions are used.
- No cards are padded with duplicates or unsupported claims.
- Any source limitation or count shortfall is reported to the user outside `cards.json`.
