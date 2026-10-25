# Working on the public edition

## Layout

- `demo.py`: local HTTP server and the single aria2 sample integration.
- `data/games.json`: fictional catalogue entries.
- `web/app.js`: navigation, catalogue, library, profiles and backups.
- `web/state.js`: local preference schema and backup validation.
- `web/style.css`: interface styles and responsive layouts.
- `main.js`: optional Electron window.
- `tests/test_demo.py`: local request boundary checks.
- `examples/`: standalone code examples; `tests/test_examples.py` runs them.

## Add a sample game

Add a unique lowercase ID, name, genre, description, colour, year, tags and collection to the JSON catalogue. Use invented names and descriptions. Covers are drawn with CSS. The local backend automatically makes a text sample available for that ID. Update the catalogue test when changing its size.

## Frontend changes

Run `python demo.py`, edit the files in `web` and reload your browser. There is no bundler or Python package installation. The interface uses DOM text nodes rather than rendering imported HTML. Keep all interface labels in English and retain keyboard access and small-screen layouts.

## Local state

The current backup format is version 1. Validate new fields in `state.js`; bound lengths, retain only known IDs and ignore unsupported fields. A restore must not read files, fetch URLs or execute code described in a backup.

## Before sharing

Run the tests, check browser errors and responsive layouts, and confirm all network traffic stays on the demo's loopback origin. Never copy environment files, tokens, personal data, application builds or the private launcher's Git history into this repository.
