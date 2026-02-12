# BD2 Mod Comparison Tool

**Language / 語言：** [English](README.md) | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

A local mod comparison and management tool for **BrownDust 2**. Browse, compare mod versions from different authors with a visual interface, and merge selected versions into an output folder with one click.

## Features

- **Auto Scan** — Recursively scans the `MODS/` folder, automatically detecting Spine animation mods and image replacement mods
- **Multi-Version Comparison** — Instantly switch between previews when multiple authors have mods for the same character
- **Spine Animation Playback** — Built-in Spine Player with animation selection, play/pause, and synchronized camera
- **Selection Management** — Select desired mod versions with search, author filter, and "selected only" view
- **One-Click Merge** — Automatically copies selected mod versions to the `MODS_MERGED/` output folder
- **Multi-Language UI** — Interface supports English, Japanese, and Traditional Chinese

## Folder Structure

```
BD2_ModComparisonTool/
├── start_tool.bat            # Launch the tool (double-click)
├── ModComparisonTools/       # Tool source code
│   ├── mod_index_server.py   #   Python backend server
│   ├── mod_viewer.html       #   Frontend UI (single HTML)
│   └── vendor/               #   Third-party libraries (Spine Player)
├── MODS/                     # Mod source (user-provided)
│   ├── AuthorA/
│   │   └── <mod folder>/
│   └── AuthorB/
│       └── <mod folder>/
└── MODS_MERGED/              # Merged output (auto-generated)
```

## Requirements

- **Python 3.10+** (standard library only, no extra packages needed)
- Modern browser (Chrome / Edge / Firefox)

## Usage

### 1. Place Mods

Organize mod files by **author name** inside `MODS/`:

```
MODS/
├── AuthorA/
│   └── SomeCharacter_Skin/
│       ├── char000123.atlas
│       ├── char000123.skel (or .json)
│       └── char000123.png
└── AuthorB/
    └── SomeCharacter_AltSkin/
        ├── char000123.atlas
        └── char000123.json
```

**Supported mod formats:**
- **Spine Mod**: `.atlas` + `.skel` or `.json`
- **Image Replacement Mod**: `.modfile` + `textures/*.png`

### 2. Launch the Tool

Double-click `start_tool.bat` in the root directory. The browser will open automatically.

You can also start manually:

```bash
python ModComparisonTools/mod_index_server.py
# Then open http://localhost:8000/ModComparisonTools/mod_viewer.html
```

### 3. Interface Guide

| Feature | Description |
|---------|-------------|
| Search | Enter Mod ID or character keywords |
| Author Filter | Filter by specific author from dropdown |
| Selected Only | Show only selected mods |
| Version Switch | Click author buttons to switch preview |
| Animation | Choose animation and play / pause |
| Select / Deselect | Decide whether to use this version |

### 4. Save & Apply

- **"Save Selections"** — Saves current selection records locally
- **"Apply Selections"** — Copies selected version files to `MODS_MERGED/` folder, ready for game use

## Notes

- `MODS/` and `MODS_MERGED/` are not included in this repository; place your own mod files
- `MODS_MERGED/` is created automatically when applying selections
- Mod folders with the same name will be overwritten

## License

MIT License — see [LICENSE](LICENSE) for details.

Mod assets are copyrighted by their respective authors.
