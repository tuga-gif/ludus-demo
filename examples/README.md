# Examples

Small, self-contained examples of ideas used in Ludus 1.8. Each file runs on its own with Python 3.10+ or Node.js and uses invented data.

They are **simplified illustrations**, not the launcher's implementation. The private app adds error handling, server-side checks and integrations that are not shown here. Nothing in this folder talks to a Ludus service.

| File | What it shows |
| --- | --- |
| [`theme_to_css.py`](theme_to_css.py) | Turning a theme recipe into CSS variables, with a text contrast check |
| [`ludus_points.py`](ludus_points.py) | How Ludus Points add up from activity |
| [`name_matching.py`](name_matching.py) | Matching a game title against release names from different sources |
| [`download_engine.py`](download_engine.py) | Picking a download engine for a link |
| [`save_backups.py`](save_backups.py) | Keeping only the most recent save backups per game |
| [`extensions.js`](extensions.js) + [`extension.example.json`](extension.example.json) | Describing an extension and turning it on or off |

Run them from the repository root:

```sh
python examples/theme_to_css.py
python examples/ludus_points.py
python examples/name_matching.py
python examples/download_engine.py
python examples/save_backups.py
node examples/extensions.js
```
