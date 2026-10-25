# Ludus — Open-source demo

Ludus is a launcher for browsing games, organising downloads, personalising the interface and keeping supported saves together. The official app is available for Windows and Linux.

**Ludus 1.8 is out — and Ludus turns one.** The first beta came out on 25 October 2025. Version 1.8 adds a community inside the launcher, Ludus Points and a profile store, a redesigned theme creator, installable extensions and faster downloads. [Download it from the website](https://lludus.netlify.app) or the [Releases](https://github.com/tuga-gif/ludus-demo/releases) page.

This repository contains a separate, standalone **open-source demo**, licensed under MIT. It lets you explore local interface features and contribute without accessing the official app's private code or services. It is not the source code of the full launcher.

[Official website](https://lludus.netlify.app) · [Official Discord](https://discord.gg/XRqMF8xcPA) · [Ludus Archive](https://discord.gg/aST3SbVsXF)

Ludus Archive is not the official community server; it shares official Ludus files for developers. For help, use the official Discord.

All interface text is in English. The sample games are fictional.

## Included features

- Twelve fictional sample games, a featured game, search, genre filters and sorting.
- Game details, favourites, personal notes and play status.
- Local library with filters and summary counts.
- Two curated catalogue collections.
- A local profile with display name, initials avatar and biography.
- Light and dark themes, accent colours, compact cards and reduced motion.
- Local JSON backup export, validation, restore and preference reset.
- Actual aria2 integration for the included local sample files.
- A Python browser app and an optional Electron desktop window.

The full Ludus catalogue comes from a separate Ludus API. That service is not distributed with this demonstration. This project includes no production service integration, user accounts or cloud saves. It cannot sign in to the full app or access its data.

Only aria2 is included as a download integration. Other download engines in the full app: libtorrent, Turbo and Ready to play.

## Code examples and how Ludus works

- [`examples/`](examples) has small, runnable examples of ideas used in Ludus 1.8: theme colours, Ludus Points, title matching, choosing a download engine, save backup retention and extensions. They are simplified illustrations, not the launcher's code.
- [How Ludus works](docs/HOW_IT_WORKS.md) is a high-level tour of the app's systems.

## Run in a browser

Install Python 3.10 or newer, then run:

```sh
python demo.py
```

On Windows, `py demo.py` also works. Open the local URL printed in the terminal (`http://127.0.0.1:8791`). A stable local port keeps browser preferences available between sessions. Only one instance can use this port. You can choose another with `python demo.py --port 8793`. Stop the demo with Ctrl+C. No Python packages are required.

To try sample downloads, install aria2 separately and make `aria2c` available on PATH. Downloads are limited to the twelve included local samples and are written to `.local/downloads`. They do not download or install games. No external URL input is supported.

## Run as a desktop window

Install Node.js and Python, then run:

```sh
npm ci
npm start
```

The desktop window uses its own local port, 8792, so it can run alongside the browser demo.

If Python is not found, set `LUDUS_DEMO_PYTHON` to its executable. The demo uses its own desktop settings folder, `LudusOpenEdition`, separate from the full app.

Library, favourites, notes, profile and appearance preferences are stored locally in the browser or demo desktop window. They are not uploaded. Clearing browser data resets them.

## Checks

```sh
python -m unittest discover -s tests
node --test tests/state.test.cjs
```

The tests also run the code examples. They check that sample downloads accept only predefined demo IDs, that requests from other origins are refused, and that private files are not served.

Code is licensed under MIT. The Ludus name and logo remain Ludus branding; the code license does not grant trademark rights. aria2 and Electron are separate projects under their respective licenses. No engine binary is included.

## Project notes

- [How Ludus works](docs/HOW_IT_WORKS.md) gives a tour of the app's systems.
- [Public scope](docs/PUBLIC_SCOPE.md) explains what is included.
- [Development guide](docs/DEVELOPMENT.md) covers the public project layout.
- [Contributing](CONTRIBUTING.md) describes useful contributions.
- [Security reporting](SECURITY.md) covers reporting issues without sharing private data.

This project starts with its own repository history. Private launcher code, credentials and personal files are not included.
