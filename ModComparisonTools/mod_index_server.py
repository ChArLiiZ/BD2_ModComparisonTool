from __future__ import annotations

import json
import os
import stat
import shutil
import time
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
from pathlib import Path
from urllib.parse import urlparse

# 使用腳本所在位置計算相對路徑
SCRIPT_DIR = Path(__file__).resolve().parent  # ModComparisonTools/
BASE_DIR = SCRIPT_DIR.parent  # BD2_ModComparisonTool/
MODS_DIR = BASE_DIR / "MODS"
MERGED_DIR = BASE_DIR / "MODS_MERGED"
SELECTIONS_FILE = SCRIPT_DIR / "mod_selections.json"
HISTORY_FILE = SCRIPT_DIR / "mod_history.json"


def find_mod_ids_in_folder(folder: Path) -> list[str]:
    mod_ids = set()
    if not folder.exists():
        return []

    atlas_files = list(folder.rglob("*.atlas"))
    for atlas in atlas_files:
        stem = atlas.stem
        json_candidate = next(folder.rglob(f"{stem}.json"), None)
        skel_candidate = next(folder.rglob(f"{stem}.skel"), None)
        if json_candidate or skel_candidate:
            mod_ids.add(stem)

    return sorted(mod_ids)


def find_mod_files(mod_folder: Path, mod_id: str) -> dict:
    """
    Find mod files in a folder. mod_id matching is case-insensitive.
    """
    files = {
        "atlas": None,
        "json": None,       # Spine JSON (.json)
        "skel": None,       # Spine binary (.skel)
        "modfile": None,    # Mod config file (.modfile) - NOT Spine data
        "pngs": [],
        "modType": "spine",  # "spine" or "image"
    }
    if not mod_folder.exists():
        return files

    mod_id_lower = mod_id.lower()

    # Build case-insensitive file lookup for this folder
    files_in_folder: dict[str, Path] = {}
    for f in mod_folder.iterdir():
        if f.is_file():
            files_in_folder[f.name.lower()] = f

    # Check for .modfile (mod configuration, not Spine data)
    modfile_key = f"{mod_id_lower}.modfile"
    if modfile_key in files_in_folder:
        modfile_path = files_in_folder[modfile_key]
        if modfile_path.stat().st_size > 10:
            files["modfile"] = modfile_path

    # Search for spine files (case-insensitive on stem)
    for file_path in mod_folder.rglob("*"):
        if not file_path.is_file():
            continue
        suffix = file_path.suffix.lower()
        if suffix not in {".atlas", ".json", ".skel", ".png"}:
            continue

        stem_lower = file_path.stem.lower()
        if suffix == ".atlas" and stem_lower == mod_id_lower:
            files["atlas"] = file_path
        elif suffix == ".json" and stem_lower == mod_id_lower and not file_path.name.lower().endswith(".jsonbk"):
            # Real Spine JSON file
            files["json"] = file_path
        elif suffix == ".skel" and stem_lower == mod_id_lower:
            files["skel"] = file_path
        elif suffix == ".png" and stem_lower.startswith(mod_id_lower):
            files["pngs"].append(file_path)

    # Determine mod type
    has_spine_data = files["atlas"] and (files["json"] or files["skel"])
    
    if has_spine_data:
        files["modType"] = "spine"
    elif files["modfile"]:
        # Image-only mod - look for textures
        files["modType"] = "image"
        textures_folder = mod_folder / "textures"
        if textures_folder.exists():
            texture_pngs = list(textures_folder.glob("*.png"))
            if texture_pngs:
                files["pngs"].extend(texture_pngs)
        # Also check for pngs directly in the mod folder
        if not files["pngs"]:
            direct_pngs = list(mod_folder.glob("*.png"))
            if direct_pngs:
                files["pngs"].extend(direct_pngs)
    
    return files


def compute_suffixes(folder_names: list[str]) -> dict[str, str]:
    if len(folder_names) <= 1:
        return {name: "" for name in folder_names}

    prefix = os.path.commonprefix(folder_names)
    suffixes = {}
    for name in folder_names:
        suffix = name[len(prefix):].lstrip("_- ")
        if not suffix:
            suffix = name
        elif prefix.lower().endswith("v") and suffix[:1].isdigit():
            suffix = f"v{suffix}"
        suffixes[name] = suffix
    return suffixes


def load_history() -> dict:
    if not HISTORY_FILE.exists():
        return {}
    try:
        content = HISTORY_FILE.read_text(encoding="utf-8")
        return json.loads(content)
    except Exception:
        return {}


def save_history(history: dict) -> None:
    try:
        HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        HISTORY_FILE.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        print(f"Error saving history: {e}")


def find_file_case_insensitive(folder: Path, filename: str) -> Path | None:
    """Find a file in folder with case-insensitive matching."""
    filename_lower = filename.lower()
    for f in folder.iterdir():
        if f.is_file() and f.name.lower() == filename_lower:
            return f
    return None


def find_mod_leaf_folders(author_dir: Path) -> dict[str, list[Path]]:
    """
    Scans an author directory to find leaf folders that DIRECTLY contain mod files.
    Returns a dict mapping mod_id -> list of folder paths.
    """
    mod_folders = {}
    if not author_dir.exists():
        return mod_folders

    # Walk the directory tree
    for root, _, files in os.walk(author_dir):
        root_path = Path(root)
        
        # Check for .atlas files in this specific directory (non-recursive)
        atlas_files = list(root_path.glob("*.atlas"))
        
        # Check for .modfile (non-recursive)
        modfile_files = list(root_path.glob("*.modfile"))
        
        if not atlas_files and not modfile_files:
            continue
        
        # Build a case-insensitive lookup of all files in this folder
        files_lower_map: dict[str, Path] = {}
        for f in root_path.iterdir():
            if f.is_file():
                files_lower_map[f.name.lower()] = f
            
        # Collect potential mod stems (normalized to lowercase for grouping)
        stems_map: dict[str, str] = {}  # lowercase -> original stem
        for f in atlas_files:
            stems_map[f.stem.lower()] = f.stem
        for f in modfile_files:
            if f.stat().st_size > 10:
                stem_lower = f.stem.lower()
                if stem_lower not in stems_map:
                    stems_map[stem_lower] = f.stem
        
        # Verify each stem (case-insensitive)
        for stem_lower, original_stem in stems_map.items():
            has_atlas = f"{stem_lower}.atlas" in files_lower_map
            has_json = f"{stem_lower}.json" in files_lower_map
            has_skel = f"{stem_lower}.skel" in files_lower_map
            has_valid_modfile = f"{stem_lower}.modfile" in files_lower_map
            
            # Valid mod if:
            # 1. Spine mod: Has atlas + (json OR skel)
            # 2. Image mod: Has valid modfile (texture replacement)
            
            is_valid = False
            if has_atlas and (has_json or has_skel):
                is_valid = True  # Spine mod
            elif has_valid_modfile:
                is_valid = True  # Image mod
            
            if is_valid:
                # Use lowercase as the canonical mod_id
                if stem_lower not in mod_folders:
                    mod_folders[stem_lower] = []
                mod_folders[stem_lower].append(root_path)

    return mod_folders


def build_config() -> dict:
    mods = []
    history = load_history()

    if not MODS_DIR.exists():
        return {"mods": mods, "authors": []}

    authors = []
    # Map (Author, ModID) -> List of folder names (leaves)
    author_mod_leaves: dict[tuple[str, str], list[str]] = {}

    # First pass: Collect all authors and their mod leaf folders
    for author_dir in sorted([p for p in MODS_DIR.iterdir() if p.is_dir()], key=lambda p: p.name.lower()):
        author = author_dir.name
        authors.append(author)
        
        leaf_map = find_mod_leaf_folders(author_dir)
        for mod_id, folders in leaf_map.items():
            for folder in folders:
                author_mod_leaves.setdefault((author, mod_id), []).append(folder.name)

    # Second pass: Build mod entries
    for author_dir in sorted([p for p in MODS_DIR.iterdir() if p.is_dir()], key=lambda p: p.name.lower()):
        author = author_dir.name
        leaf_map = find_mod_leaf_folders(author_dir)
        
        for mod_id, folders in leaf_map.items():
            for mod_folder in folders:
                files = find_mod_files(mod_folder, mod_id)
                # Validation: 
                # - Spine mod: needs atlas + (json OR skel)
                # - Image mod: needs modfile (+ optional pngs)
                has_spine = files["atlas"] and (files["json"] or files["skel"])
                has_image = files["modfile"] is not None
                if not has_spine and not has_image:
                    continue

                mod_entry = next((m for m in mods if m["id"] == mod_id), None)
                if not mod_entry:
                    mod_entry = {"id": mod_id, "name": mod_id, "versions": []}
                    mods.append(mod_entry)

                def rel_path(path: Path | None) -> str | None:
                    if path is None:
                        return None
                    return path.relative_to(BASE_DIR).as_posix()

                # Suffix based on folder names of siblings for the same mod/author
                suffix_map = compute_suffixes(author_mod_leaves.get((author, mod_id), []))
                suffix = suffix_map.get(mod_folder.name, "")
                author_label = f"{author} {suffix}".strip()

                # relative_path is now from author_dir to the LEAF folder
                relative_path = mod_folder.relative_to(author_dir).as_posix()
                
                mod_entry["versions"].append(
                    {
                        "author": author,
                        "authorLabel": author_label,
                        "versionId": f"{author}::{relative_path}",
                        "relativePath": relative_path,
                        "folderName": mod_folder.name,
                        "modType": files["modType"],
                        "atlas": rel_path(files["atlas"]),
                        "json": rel_path(files["json"]),
                        "skel": rel_path(files["skel"]),
                        "pngs": [rel_path(p) for p in files["pngs"] if p],
                    }
                )

    mods.sort(key=lambda m: m["id"].lower())

    # Flag new/updated mods
    for mod in mods:
        current_count = len(mod["versions"])
        history_entry = history.get(mod["id"])

        if not history_entry:
            mod["isNew"] = True
        elif current_count > history_entry.get("versionCount", 0):
            mod["isUpdated"] = True

    return {"mods": mods, "authors": authors}


def _robust_rmtree(path: Path, max_retries: int = 3, delay: float = 0.5) -> None:
    """Remove a directory tree with retry logic for Windows file-locking issues.

    On Windows, files may be temporarily locked by Explorer, antivirus, or the
    Spine WebGL player.  This helper:
      1. Clears read-only flags that sometimes prevent deletion.
      2. Retries up to *max_retries* times with an increasing delay.
    """
    def _on_exc(func, fpath, exc_info) -> None:  # noqa: ANN001
        """Handle permission errors by removing read-only flag and retrying."""
        os.chmod(fpath, stat.S_IWRITE)
        func(fpath)

    for attempt in range(max_retries):
        try:
            shutil.rmtree(path, onexc=_on_exc)
            return
        except PermissionError:
            if attempt < max_retries - 1:
                wait = delay * (attempt + 1)
                print(f"[rmtree] PermissionError on '{path.name}', retrying in {wait:.1f}s "
                      f"(attempt {attempt + 1}/{max_retries})...")
                time.sleep(wait)
            else:
                print(f"[rmtree] Failed to remove '{path.name}' after {max_retries} attempts.")
                raise


def merge_selected_mods(selections: dict[str, dict]) -> None:
    MERGED_DIR.mkdir(parents=True, exist_ok=True)
    if not MODS_DIR.exists():
        return

    # Track which folder names should exist in MODS_MERGED
    active_folders = set()
    
    # Deduplicate selections by lowercase mod_id (keep the last one)
    # This handles cases where the same mod ID appears with different cases
    normalized_selections: dict[str, tuple[str, dict]] = {}
    for mod_id, selection in selections.items():
        mod_id_lower = mod_id.lower()
        normalized_selections[mod_id_lower] = (mod_id, selection)

    for mod_id_lower, (mod_id, selection) in normalized_selections.items():
        author = selection.get("author")
        relative_path = selection.get("relativePath")
        # Ensure we have folderName stored in selection, OR re-derive it
        # Wait, frontend sends {versionId, author, label, relativePath}. It might NOT send folderName.
        # But relativePath includes the leaf folder name at the end.
        
        if not author or not relative_path:
            continue

        author_dir = MODS_DIR / author
        if not author_dir.exists():
            continue

        source_folder = author_dir / relative_path
        if not source_folder.exists():
            continue

        folder_name = source_folder.name
        active_folders.add(folder_name)

        destination = MERGED_DIR / folder_name
        if destination.exists():
            # If it already exists, we might need to overwrite it IF it's different.
            # Simple approach: Always remove and re-copy to ensure it matches current selection.
            # Optimization: Check if source and dest match? No, just copy.
            _robust_rmtree(destination)

        shutil.copytree(source_folder, destination)

    # Clean up orphan folders in MODS_MERGED
    for item in MERGED_DIR.iterdir():
        if item.is_dir() and item.name not in active_folders:
            try:
                _robust_rmtree(item)
                print(f"Removed orphan folder: {item.name}")
            except Exception as e:
                print(f"Failed to remove orphan folder {item.name}: {e}")


class ModIndexHandler(SimpleHTTPRequestHandler):
    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/mods_index.json":
            payload = build_config()
            content = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return
        if parsed.path == "/mod_selections.json":
            if SELECTIONS_FILE.exists():
                content = SELECTIONS_FILE.read_bytes()
            else:
                content = b"{}"
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return
        if parsed.path == "/mark_all_read":
            config = build_config()
            history = {}
            for mod in config["mods"]:
                history[mod["id"]] = {"versionCount": len(mod["versions"])}
            save_history(history)
            
            response = json.dumps({"status": "ok"}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(response)))
            self.end_headers()
            self.wfile.write(response)
            return
        super().do_GET()

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/apply_selections":
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length)
        try:
            payload = json.loads(body.decode("utf-8"))
        except json.JSONDecodeError:
            self.send_response(400)
            self.end_headers()
            return

        selections = payload.get("selections")
        if not isinstance(selections, dict):
            self.send_response(400)
            self.end_headers()
            return

        SELECTIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
        SELECTIONS_FILE.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        merge_selected_mods(selections)

        response = json.dumps({"status": "ok"}, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)


if __name__ == "__main__":
    os.chdir(BASE_DIR)

    # Explicitly add .modfile as application/json to the extensions_map of SimpleHTTPRequestHandler
    SimpleHTTPRequestHandler.extensions_map[".modfile"] = "application/json"

    with TCPServer(("", 8000), ModIndexHandler) as httpd:
        print("Serving on http://localhost:8000")
        httpd.serve_forever()
