# How Ludus works

A high-level tour of the systems in Ludus 1.8. It explains what each part does, not how the private launcher is built. Where a simplified example exists, it is linked.

## The launcher

Ludus is a desktop app for Windows and Linux. A small local backend serves the interface and does the work on your computer: finding games, managing downloads, launching games and backing up saves. The window talks only to that local backend.

## Catalogue and sources

The catalogue lists games with artwork, genres and descriptions. **Sources** are JSON lists of releases that you add yourself from the [source directory](https://lludus.netlify.app/sources). When you search for a game, Ludus looks through every source you've added and matches release names to the game's title.

Release names are messy — extra words, Roman numerals, version numbers — so titles are normalised before they're compared. See [`examples/name_matching.py`](../examples/name_matching.py).

## Downloads

Each download uses an engine suited to the link: a torrent engine for magnets and `.torrent` files, aria2 for direct links, a parallel "Turbo" mode for file hosts, and **Ready to play**, which installs the game when the download ends. Downloads resume after interruptions. See [`examples/download_engine.py`](../examples/download_engine.py).

This demo includes a real aria2 integration limited to its own sample files.

## Themes

A theme starts from three colours — background, text and accent — and the rest of the palette is derived from them. The theme creator in 1.8 shows a large live preview, can build palettes from one colour or an image, and supports undo and redo. Themes can be shared through a GitHub repository and installed from the public assets page. See [`examples/theme_to_css.py`](../examples/theme_to_css.py).

## Extensions

Extensions are optional features you turn on in the app: FPS overlay, keyboard shortcuts, a command palette, download alerts, in-game download progress, automatic save backups and game collections. They come from a list shipped with Ludus; no code is downloaded. See [`examples/extensions.js`](../examples/extensions.js).

## Saves

With cloud saves connected, supported games are backed up when you close them. The automatic save backup extension also keeps local compressed copies — the five most recent per game. See [`examples/save_backups.py`](../examples/save_backups.py).

## Community and Ludus Points

The community has a feed of posts and reviews, player rankings and game activity. **Ludus Points** are earned by using Ludus — time in the app, finished downloads, completed games, posts and daily visits — and spent in the profile store on backgrounds, frames, titles and effects. Points are confirmed by the server, so the calculation in [`examples/ludus_points.py`](../examples/ludus_points.py) only shows the arithmetic.

## Updates

On Windows, Ludus checks for new versions and offers to install them. Installers are published on the [Releases](https://github.com/tuga-gif/ludus-demo/releases) page with their SHA-256 checksums.

## What is not here

The full catalogue service, accounts, the community backend, the profile store and the private launcher code are not part of this repository.
