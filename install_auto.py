#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
chuanban Obsidian Full Suite — Cross-Platform Zero-Config Auto Installer (v1.1.0 Opus-Hardened)
Automatically discovers Obsidian vaults (macOS / Windows / Linux), installs & registers
bundled fonts, deploys the chuanban theme + preset switcher plugin + snippet,
and non-destructively merges them into Obsidian's JSON configuration files with
timestamped backups, atomic writes, and machine-readable status reporting.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

GDRIVE_FONT_FOLDER_URL = "https://drive.google.com/drive/folders/1NX92SgVUqtSjWg6bt6sIJXy-cn7J_boC"

REMOTE_ANTHROPIC_FONTS: List[Dict[str, Any]] = [
    {
        "name": "AnthropicMono-Regular.ttf",
        "id": "1NK_1Q2MBl5yHw94pC_kbzybDgqEFCZVk",
        "size": 149556,
        "sha256": "0e686e9d651bf3b7448bbc7ec5c5ffd48e3ae9b07710d26ed332170487f60295",
    },
    {
        "name": "AnthropicSans-Regular.ttf",
        "id": "1IwmkmuLNmHrqq6jAQxso46FXN9XgDAVo",
        "size": 310084,
        "sha256": "6b95f2701784e79c30334668c85077c187c66ef0e0b105647a27c253ff41fb32",
    },
    {
        "name": "AnthropicSans-Bold.ttf",
        "id": "1VyJi_4qCy2DrZvo_V_ShpUrbHbjL1MwG",
        "size": 310084,
        "sha256": "a79cf47de0f8e8165e048e742d97c5ec9488e09d7af5ddde20efdbfb75a4993b",
    },
    {
        "name": "AnthropicSerif-Regular.ttf",
        "id": "1RZ1rMYYFlr5B-slSSZV-DCJtv5AfTMUV",
        "size": 510352,
        "sha256": "5806e7fbfebfe6683fdb2c16d8eb91b98ccd6b4ba0d477e8f5167782e0d7b009",
    },
    {
        "name": "AnthropicSerif-Bold.ttf",
        "id": "1-LJfTa1wasIqkoCCHI4mfVyh8tzreiAO",
        "size": 510352,
        "sha256": "3e0d9660390f1800f229e2724cf0b09030ec53188cd3d361ca210077ce564426",
    },
]


class ConfigParseError(Exception):
    """Raised when an existing Obsidian JSON config file is malformed and must not be overwritten."""


def configure_utf8_stdio() -> None:
    """P0-2 Fix: Force UTF-8 on stdout/stderr so piped Agent execution on Windows (GBK/cp1252) never crashes."""
    for stream in (sys.stdout, sys.stderr):
        try:
            if hasattr(stream, "reconfigure"):
                stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def get_obsidian_config_candidates() -> List[Path]:
    """Return candidate paths for Obsidian's global obsidian.json registry across OSes and package formats."""
    system = platform.system()
    home = Path.home()
    if system == "Darwin":
        return [home / "Library" / "Application Support" / "obsidian" / "obsidian.json"]
    elif system == "Windows":
        appdata = os.environ.get("APPDATA", str(home / "AppData" / "Roaming"))
        return [Path(appdata) / "obsidian" / "obsidian.json"]
    else:
        xdg = os.environ.get("XDG_CONFIG_HOME", str(home / ".config"))
        return [
            Path(xdg) / "obsidian" / "obsidian.json",
            home / ".var" / "app" / "md.obsidian.Obsidian" / "config" / "obsidian" / "obsidian.json",
            home / "snap" / "obsidian" / "current" / ".config" / "obsidian" / "obsidian.json",
        ]


def discover_vaults(only_open: bool = False) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    P1-1 & P1-2 Fix: Discover vaults from obsidian.json using utf-8-sig and per-vault try/except OSError
    so a single TCC/permission-blocked vault never aborts discovery of other vaults.
    """
    discovered: List[Dict[str, Any]] = []
    seen_paths = set()
    warnings: List[str] = []

    for cfg_path in get_obsidian_config_candidates():
        try:
            if not cfg_path.exists():
                continue
        except OSError as e:
            warnings.append(f"Cannot access {cfg_path}: {e}")
            continue

        try:
            raw = cfg_path.read_text(encoding="utf-8-sig")
            data = json.loads(raw)
        except Exception as e:
            warnings.append(f"Failed to parse {cfg_path}: {e}")
            continue

        vaults_dict = data.get("vaults", {})
        if not isinstance(vaults_dict, dict):
            continue

        for vid, vinfo in vaults_dict.items():
            if not isinstance(vinfo, dict):
                continue
            raw_path = vinfo.get("path")
            if not raw_path:
                continue
            is_open = bool(vinfo.get("open", False))
            if only_open and not is_open:
                continue
            try:
                vp = Path(raw_path).expanduser().resolve()
                if str(vp) in seen_paths:
                    continue
                if vp.is_dir() and (vp / ".obsidian").is_dir():
                    seen_paths.add(str(vp))
                    discovered.append({"id": vid, "path": vp, "open": is_open})
                else:
                    warnings.append(f"Vault path missing or has no .obsidian directory: {raw_path}")
            except OSError as e:
                warnings.append(f"Permission/OS error accessing vault '{raw_path}': {e}")

    return discovered, warnings


def is_obsidian_running() -> bool:
    """Check if Obsidian process is currently running (to warn about config writeback & font cache)."""
    system = platform.system()
    try:
        if system == "Darwin":
            res = subprocess.run(["pgrep", "-x", "Obsidian"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return res.returncode == 0
        elif system == "Windows":
            res = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq Obsidian.exe", "/NH"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            return "obsidian.exe" in (res.stdout or "").lower()
        else:
            res = subprocess.run(["pgrep", "-f", "obsidian"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return res.returncode == 0
    except Exception:
        return False


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def preflight_suite(suite_dir: Path) -> List[str]:
    """Verify all required suite assets exist before touching any user files."""
    required = [
        suite_dir / "theme" / "chuanban" / "theme.css",
        suite_dir / "theme" / "chuanban" / "manifest.json",
        suite_dir / "plugins" / "chuanban-preset-switcher" / "main.js",
        suite_dir / "plugins" / "chuanban-preset-switcher" / "manifest.json",
        suite_dir / "snippets" / "preset-notion-serif.css",
        suite_dir / "config" / "page-preview.json",
    ]
    missing = [str(p.relative_to(suite_dir)) for p in required if not p.is_file() or p.stat().st_size == 0]
    return missing


def install_fonts(suite_dir: Path, dry_run: bool = False) -> Tuple[str, List[str]]:
    """
    Decoupled Font Installer (v1.2):
    - Fonts are NOT bundled inside the git repo/package; instead they are hosted in the shared
      Google Drive folder (GDRIVE_FONT_FOLDER_URL).
    - For each font in REMOTE_ANTHROPIC_FONTS:
      1) If already installed in OS user font dir (matching SHA-256), keep it.
      2) Else if user pre-downloaded it into <suite_dir>/fonts/<name>, copy from there.
      3) Else automatically download from Google Drive direct link and verify SHA-256.
    - On Windows: registers each font under HKCU\\Software\\Microsoft\\Windows NT\\CurrentVersion\\Fonts
      and calls gdi32.AddFontResourceW + broadcasts WM_FONTCHANGE.
    - On Linux: runs fc-cache -f if available.
    Returns (status: 'registered'|'copied_only'|'manual_download_needed'|'failed', warnings).
    """
    fonts_src = suite_dir / "fonts"
    warnings: List[str] = []

    system = platform.system()
    home = Path.home()
    if system == "Darwin":
        font_dest = home / "Library" / "Fonts"
    elif system == "Windows":
        localappdata = os.environ.get("LOCALAPPDATA", str(home / "AppData" / "Local"))
        font_dest = Path(localappdata) / "Microsoft" / "Windows" / "Fonts"
    else:
        font_dest = home / ".local" / "share" / "fonts"

    if dry_run:
        print(f"[DRY-RUN] Would check/download {len(REMOTE_ANTHROPIC_FONTS)} font file(s) from Google Drive -> {font_dest}")
        return "registered", warnings

    try:
        font_dest.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        return "failed", [f"Cannot create font directory {font_dest}: {e}"]

    copied_paths: List[Path] = []
    missing_remote: List[str] = []

    for item in REMOTE_ANTHROPIC_FONTS:
        fname = item["name"]
        fid = item["id"]
        expected_sha = item["sha256"]
        target = font_dest / fname
        local_candidate = fonts_src / fname

        # 1. Check if already present in OS font directory
        try:
            if target.is_file() and target.stat().st_size > 0 and file_sha256(target) == expected_sha:
                copied_paths.append(target)
                continue
        except OSError:
            pass

        # 2. Check if user pre-downloaded into <suite_dir>/fonts/
        if local_candidate.is_file() and local_candidate.stat().st_size > 0:
            try:
                shutil.copy2(local_candidate, target)
                copied_paths.append(target)
                continue
            except PermissionError:
                if target.exists() and target.stat().st_size > 0:
                    copied_paths.append(target)
                    continue
            except OSError as e:
                warnings.append(f"Failed copying local {fname} -> {target}: {e}")

        # 3. Download from Google Drive direct URL
        dl_url = f"https://drive.google.com/uc?export=download&id={fid}"
        try:
            req = urllib.request.Request(dl_url, headers={"User-Agent": "Mozilla/5.0 chuanban-installer/1.2"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = resp.read()
            actual_sha = hashlib.sha256(data).hexdigest()
            if actual_sha != expected_sha:
                warnings.append(
                    f"Downloaded {fname} from Google Drive but SHA-256 mismatched (got {actual_sha[:12]}...). "
                    f"Please download manually from {GDRIVE_FONT_FOLDER_URL}"
                )
                missing_remote.append(fname)
                continue
            tmp_target = target.with_name(f"{target.name}.tmp.{os.getpid()}")
            tmp_target.write_bytes(data)
            os.replace(tmp_target, target)
            copied_paths.append(target)
        except PermissionError:
            if target.exists() and target.stat().st_size > 0:
                copied_paths.append(target)
            else:
                missing_remote.append(fname)
        except Exception as e:
            missing_remote.append(fname)
            warnings.append(
                f"Could not auto-download {fname} from Google Drive ({e}). "
                f"Please download from: {GDRIVE_FONT_FOLDER_URL}"
            )

    if missing_remote and not copied_paths:
        return "manual_download_needed", warnings

    status = "registered" if not missing_remote else "manual_download_needed"
    if system == "Windows":
        reg_ok = True
        try:
            import ctypes
            import winreg  # type: ignore

            reg_path = r"Software\Microsoft\Windows NT\CurrentVersion\Fonts"
            with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_SET_VALUE) as key:
                for p in copied_paths:
                    val_name = f"{p.stem} (TrueType)"
                    winreg.SetValueEx(key, val_name, 0, winreg.REG_SZ, str(p))
            try:
                gdi32 = ctypes.windll.gdi32  # type: ignore
                user32 = ctypes.windll.user32  # type: ignore
                for p in copied_paths:
                    gdi32.AddFontResourceW(str(p))
                HWND_BROADCAST = 0xFFFF
                WM_FONTCHANGE = 0x001D
                SMTO_ABORTIFHUNG = 0x0002
                result = ctypes.c_ulong()
                user32.SendMessageTimeoutW(HWND_BROADCAST, WM_FONTCHANGE, 0, 0, SMTO_ABORTIFHUNG, 1000, ctypes.byref(result))
            except Exception as e:
                warnings.append(f"Windows GDI font broadcast warning (reboot/re-login may be needed): {e}")
        except Exception as e:
            reg_ok = False
            status = "copied_only"
            warnings.append(f"Windows HKCU font registry write failed: {e}")
        if reg_ok:
            print(f"[OK] Installed & registered {len(copied_paths)} Anthropic (.ttf) font file(s) -> {font_dest}")
        else:
            print(f"[WARN] Copied {len(copied_paths)} font file(s) to {font_dest}, but registry registration had warnings")
    elif system == "Linux":
        print(f"[OK] Installed {len(copied_paths)} Anthropic (.ttf) font file(s) -> {font_dest}")
        fc_cache = shutil.which("fc-cache")
        if fc_cache:
            try:
                subprocess.run([fc_cache, "-f", str(font_dest)], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception as e:
                warnings.append(f"fc-cache failed: {e}")
        else:
            status = "copied_only"
            warnings.append("fc-cache not found; run 'fc-cache -f' manually if fonts do not appear")
    else:
        print(f"[OK] Installed {len(copied_paths)} Anthropic (.ttf) font file(s) -> {font_dest}")

    return status, warnings


def backup_file_timestamped(path: Path) -> Optional[Path]:
    """Create a timestamped .bak copy before modifying an existing config file."""
    if not path.exists():
        return None
    ts = time.strftime("%Y%m%d-%H%M%S")
    bak = path.with_name(f"{path.name}.{ts}.bak")
    counter = 1
    while bak.exists():
        bak = path.with_name(f"{path.name}.{ts}.{counter}.bak")
        counter += 1
    shutil.copy2(path, bak)
    return bak


def read_json_safe(path: Path, default_factory: Callable[[], Any], expected_type: type) -> Any:
    """
    P0-1 Fix: Read JSON using utf-8-sig (handles UTF-8 BOM).
    If the file exists and fails to parse or has the wrong root type, back it up and raise ConfigParseError.
    NEVER silently reset or overwrite a user's existing config!
    """
    if not path.exists():
        return default_factory()
    try:
        raw = path.read_text(encoding="utf-8-sig").strip()
        if not raw:
            return default_factory()
        data = json.loads(raw)
    except Exception as e:
        bak = backup_file_timestamped(path)
        raise ConfigParseError(f"Malformed JSON in {path} (backed up to {bak}): {e}")

    if not isinstance(data, expected_type):
        bak = backup_file_timestamped(path)
        raise ConfigParseError(
            f"Unexpected JSON root type {type(data).__name__} in {path} (expected {expected_type.__name__}, backed up to {bak})"
        )
    return data


def write_json_atomic(path: Path, data: Any) -> None:
    """P2 Fix: Atomic write via temporary file + os.replace, UTF-8 without BOM."""
    tmp = path.with_name(f"{path.name}.tmp.{os.getpid()}")
    content = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, path)


def verify_vault_installation(vault_path: Path) -> Tuple[bool, List[str]]:
    """Verify all 5 asset files and 3 JSON configs in a vault."""
    obs_dir = vault_path / ".obsidian"
    errors: List[str] = []
    required_files = [
        obs_dir / "themes" / "chuanban" / "theme.css",
        obs_dir / "themes" / "chuanban" / "manifest.json",
        obs_dir / "plugins" / "chuanban-preset-switcher" / "main.js",
        obs_dir / "plugins" / "chuanban-preset-switcher" / "manifest.json",
        obs_dir / "snippets" / "preset-notion-serif.css",
    ]
    for rf in required_files:
        if not rf.is_file() or rf.stat().st_size == 0:
            errors.append(f"Missing or empty file: {rf}")

    try:
        app_data = read_json_safe(obs_dir / "appearance.json", dict, dict)
        if app_data.get("cssTheme") != "chuanban":
            errors.append(f"appearance.json cssTheme is '{app_data.get('cssTheme')}' (expected 'chuanban')")
    except Exception as e:
        errors.append(str(e))

    try:
        cp_data = read_json_safe(obs_dir / "community-plugins.json", list, list)
        if "chuanban-preset-switcher" not in cp_data:
            errors.append("community-plugins.json does not contain 'chuanban-preset-switcher'")
    except Exception as e:
        errors.append(str(e))

    return len(errors) == 0, errors


def install_to_vault(
    suite_dir: Path,
    vault_path: Path,
    default_preset: Optional[str] = None,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    Deploy theme, plugin, snippet, and non-destructively update JSON configs for a single vault.
    Returns a structured status dictionary for machine-readable reporting.
    """
    obs_dir = vault_path / ".obsidian"
    result: Dict[str, Any] = {
        "path": str(vault_path),
        "status": "fail",
        "restricted_mode_suspected": False,
        "backups": [],
        "warnings": [],
        "error": None,
    }

    try:
        if not vault_path.is_dir() or not obs_dir.is_dir():
            result["error"] = f"Not a valid Obsidian vault (missing .obsidian directory): {vault_path}"
            print(f"[ERROR] {result['error']}")
            return result
    except OSError as e:
        result["error"] = f"OS error accessing vault {vault_path}: {e}"
        print(f"[ERROR] {result['error']}")
        return result

    print(f"\n[VAULT] Configuring Obsidian Vault: {vault_path}")

    # Pre-read & validate all target JSON configs BEFORE copying or mutating anything
    app_path = obs_dir / "appearance.json"
    cp_path = obs_dir / "community-plugins.json"
    pp_path = obs_dir / "page-preview.json"
    core_path = obs_dir / "core-plugins.json"

    try:
        app_data = read_json_safe(app_path, dict, dict)
        cp_existed = cp_path.exists()
        cp_data = read_json_safe(cp_path, list, list)
        pp_data = read_json_safe(pp_path, dict, dict)
        bundle_pp = read_json_safe(suite_dir / "config" / "page-preview.json", dict, dict)
        core_data = read_json_safe(core_path, lambda: None, object) if core_path.exists() else None
    except ConfigParseError as e:
        result["error"] = str(e)
        print(f"   [ERROR] Aborting vault {vault_path} to protect existing settings: {e}")
        return result

    # Detect whether Restricted Mode is likely active (community-plugins.json didn't exist or was empty)
    if (not cp_existed) or len(cp_data) == 0:
        result["restricted_mode_suspected"] = True

    if dry_run:
        print(f"   [DRY-RUN] Would deploy theme, plugin, snippet, and merge JSON configs in {obs_dir}")
        result["status"] = "ok"
        return result

    try:
        # 1. Copy Theme
        theme_dest = obs_dir / "themes" / "chuanban"
        theme_dest.mkdir(parents=True, exist_ok=True)
        shutil.copy2(suite_dir / "theme" / "chuanban" / "theme.css", theme_dest / "theme.css")
        shutil.copy2(suite_dir / "theme" / "chuanban" / "manifest.json", theme_dest / "manifest.json")
        print(f"   [OK] Deployed theme -> {theme_dest}")

        # 2. Copy Plugin (chuanban-preset-switcher)
        plugin_dest = obs_dir / "plugins" / "chuanban-preset-switcher"
        plugin_dest.mkdir(parents=True, exist_ok=True)
        shutil.copy2(suite_dir / "plugins" / "chuanban-preset-switcher" / "main.js", plugin_dest / "main.js")
        shutil.copy2(suite_dir / "plugins" / "chuanban-preset-switcher" / "manifest.json", plugin_dest / "manifest.json")
        print(f"   [OK] Deployed plugin '排版预设切换器 (Chuanban Preset Switcher)' -> {plugin_dest}")

        # 3. Copy Snippet (preset-notion-serif.css)
        snippet_dest = obs_dir / "snippets"
        snippet_dest.mkdir(parents=True, exist_ok=True)
        shutil.copy2(suite_dir / "snippets" / "preset-notion-serif.css", snippet_dest / "preset-notion-serif.css")
        print(f"   [OK] Deployed companion snippet -> {snippet_dest / 'preset-notion-serif.css'}")

        # 4. Timestamped backups before modifying any JSON config
        for cfg_file in (app_path, cp_path, pp_path):
            bak = backup_file_timestamped(cfg_file)
            if bak:
                result["backups"].append(str(bak))

        # 5. Merge page-preview.json non-destructively (preserve user's other keys)
        pp_data.update(bundle_pp)
        write_json_atomic(pp_path, pp_data)
        print(f"   [OK] Merged sidebar hover preview config -> {pp_path}")

        # Ensure page-preview core plugin is enabled if core-plugins.json exists
        if isinstance(core_data, dict) and core_data.get("page-preview") is False:
            bak = backup_file_timestamped(core_path)
            if bak:
                result["backups"].append(str(bak))
            core_data["page-preview"] = True
            write_json_atomic(core_path, core_data)
            print("   [OK] Enabled core 'page-preview' plugin in core-plugins.json")
        elif isinstance(core_data, list) and "page-preview" not in core_data:
            bak = backup_file_timestamped(core_path)
            if bak:
                result["backups"].append(str(bak))
            core_data.append("page-preview")
            write_json_atomic(core_path, core_data)
            print("   [OK] Enabled core 'page-preview' plugin in core-plugins.json")

        # 6. Merge appearance.json non-destructively
        app_data["cssTheme"] = "chuanban"
        app_data.setdefault("showRibbon", True)
        snippets = app_data.get("enabledCssSnippets", [])
        if not isinstance(snippets, list):
            snippets = []
        if default_preset == "serif" and "preset-notion-serif" not in snippets:
            snippets.append("preset-notion-serif")
        elif default_preset == "typewriter" and "preset-notion-serif" in snippets:
            snippets.remove("preset-notion-serif")
        app_data["enabledCssSnippets"] = snippets
        write_json_atomic(app_path, app_data)
        print("   [OK] Activated 'chuanban' theme in appearance.json")

        # 7. Append chuanban-preset-switcher to community-plugins.json (strict superset guarantee)
        original_plugins_set = set(cp_data)
        if "chuanban-preset-switcher" not in cp_data:
            cp_data.append("chuanban-preset-switcher")
        if not original_plugins_set.issubset(set(cp_data)):
            raise RuntimeError("Internal safety check failed: community-plugins list would lose existing entries!")
        write_json_atomic(cp_path, cp_data)
        print("   [OK] Enabled 'chuanban-preset-switcher' in community-plugins.json")

        # 8. Post-install verification on this vault
        ok, verify_errors = verify_vault_installation(vault_path)
        if not ok:
            result["status"] = "fail"
            result["error"] = "; ".join(verify_errors)
            print(f"   [ERROR] Post-install verification failed: {result['error']}")
            return result

        result["status"] = "ok"
        return result

    except Exception as e:
        result["status"] = "fail"
        result["error"] = str(e)
        print(f"   [ERROR] Failed configuring vault {vault_path}: {e}")
        return result


def main() -> None:
    configure_utf8_stdio()

    parser = argparse.ArgumentParser(description="chuanban Obsidian Full Suite Auto-Installer (v1.1.0)")
    parser.add_argument("vaults", nargs="*", help="Explicit Obsidian vault paths (if omitted, targets currently open vaults, or use --all)")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Install to ALL discovered vaults (including closed vaults)",
    )
    parser.add_argument(
        "--preset",
        choices=["typewriter", "serif"],
        default=None,
        help="Force initial typography preset ('typewriter' or 'serif'; default preserves current snippet state)",
    )
    parser.add_argument("--list", action="store_true", help="List discovered Obsidian vaults and exit without modifying anything")
    parser.add_argument("--dry-run", action="store_true", help="Simulate installation without modifying files")
    parser.add_argument("--verify", action="store_true", help="Verify existing installation in target vaults and exit")
    args = parser.parse_args()

    suite_dir = Path(__file__).resolve().parent

    # Mode 1: --list
    if args.list:
        discovered, warnings = discover_vaults(only_open=False)
        for w in warnings:
            print(f"[WARN] {w}")
        if not discovered:
            print("No Obsidian vaults discovered in standard obsidian.json locations.")
            print("CHUANBAN_VAULTS=[]")
            sys.exit(1)
        print(f"Discovered {len(discovered)} Obsidian vault(s):")
        for idx, item in enumerate(discovered, 1):
            state_str = "OPEN" if item["open"] else "closed"
            print(f"  {idx}. [{state_str}] {item['path']}")
        print("CHUANBAN_VAULTS=" + json.dumps([{"path": str(x["path"]), "open": x["open"]} for x in discovered], ensure_ascii=False))
        sys.exit(0)

    # Resolve target vaults
    discovery_warnings: List[str] = []
    if args.vaults:
        target_vaults = [Path(p).expanduser().resolve() for p in args.vaults]
    else:
        discovered, discovery_warnings = discover_vaults(only_open=False)
        if args.all or len(discovered) <= 1:
            target_vaults = [item["path"] for item in discovered]
        else:
            open_vaults = [item["path"] for item in discovered if item["open"]]
            closed_vaults = [str(item["path"]) for item in discovered if not item["open"]]
            if open_vaults:
                target_vaults = open_vaults
                if closed_vaults:
                    print(
                        f"[INFO] Targeting {len(open_vaults)} currently OPEN vault(s). "
                        f"Skipped {len(closed_vaults)} closed vault(s) to preserve their independent themes (pass --all or explicit path to include them)."
                    )
            else:
                target_vaults = [item["path"] for item in discovered]

    for w in discovery_warnings:
        print(f"[WARN] {w}")

    # Mode 2: --verify
    if args.verify:
        if not target_vaults:
            print("[ERROR] No vaults specified or discovered to verify.")
            sys.exit(1)
        all_ok = True
        for vp in target_vaults:
            ok, errs = verify_vault_installation(vp)
            if ok:
                print(f"[VERIFY OK] {vp}")
            else:
                all_ok = False
                print(f"[VERIFY FAIL] {vp}: {'; '.join(errs)}")
        sys.exit(0 if all_ok else 1)

    # Preflight check suite integrity
    missing_assets = preflight_suite(suite_dir)
    if missing_assets:
        print(f"[ERROR] Incomplete suite package! Missing or empty files: {', '.join(missing_assets)}")
        print(
            "CHUANBAN_RESULT="
            + json.dumps({"status": "fail", "reason": "incomplete_suite", "missing": missing_assets}, ensure_ascii=False)
        )
        sys.exit(1)

    obsidian_running = is_obsidian_running()
    if obsidian_running:
        print(
            "[WARN] Obsidian is currently running. Newly installed system fonts and configuration changes "
            "require a FULL restart of Obsidian (Cmd+Q / Alt+F4 then reopen) to take full effect."
        )

    # Install fonts
    font_status, font_warnings = install_fonts(suite_dir, dry_run=args.dry_run)
    for fw in font_warnings:
        print(f"[WARN] {fw}")

    if not target_vaults:
        print("\n[ERROR] No Obsidian vaults auto-discovered. Please pass the vault path explicitly:")
        print(f'   python "{Path(__file__).name}" "/path/to/your/ObsidianVault"')
        print(
            "CHUANBAN_RESULT="
            + json.dumps(
                {
                    "status": "fail",
                    "reason": "no_vaults_found",
                    "fonts": font_status,
                    "warnings": discovery_warnings + font_warnings,
                },
                ensure_ascii=False,
            )
        )
        sys.exit(1)

    vault_results: List[Dict[str, Any]] = []
    for vp in target_vaults:
        res = install_to_vault(suite_dir, vp, default_preset=args.preset, dry_run=args.dry_run)
        vault_results.append(res)

    ok_vaults = [r for r in vault_results if r["status"] == "ok"]
    failed_vaults = [r for r in vault_results if r["status"] != "ok"]
    restricted_suspected = any(r.get("restricted_mode_suspected") for r in ok_vaults)
    has_warnings = bool(discovery_warnings or font_warnings or failed_vaults or font_status not in ("registered",))

    overall_status = "ok"
    exit_code = 0
    if not ok_vaults:
        overall_status = "fail"
        exit_code = 1
    elif failed_vaults or font_status in ("failed", "manual_download_needed", "copied_only"):
        overall_status = "partial"
        exit_code = 2

    summary_payload = {
        "status": overall_status,
        "fonts": font_status,
        "font_gdrive_url": GDRIVE_FONT_FOLDER_URL,
        "obsidian_was_running": obsidian_running,
        "restart_required": True,
        "restricted_mode_suspected": restricted_suspected,
        "vaults_ok": [r["path"] for r in ok_vaults],
        "vaults_failed": [{"path": r["path"], "error": r["error"]} for r in failed_vaults],
        "warnings": discovery_warnings + font_warnings,
    }

    print("\n" + "=" * 72)
    if overall_status == "ok":
        print(
            f"[SUCCESS] Configured {len(ok_vaults)} Obsidian vault(s). "
            "Theme 'chuanban' & plugin '排版预设切换器 (Chuanban Preset Switcher)' are active."
        )
    elif overall_status == "partial":
        print(
            f"[PARTIAL] Configured {len(ok_vaults)} vault(s), but {len(failed_vaults)} vault(s) or font steps reported errors."
        )
    else:
        print("[FAILED] No Obsidian vaults were successfully configured. See errors above.")

    if restricted_suspected:
        print(
            "[IMPORTANT] One or more vaults had no prior community plugins enabled. "
            "Please remind the user to open Obsidian Settings -> Community plugins -> Turn on community plugins (关闭安全模式)."
        )
    print("[IMPORTANT] Please completely quit and reopen Obsidian so the new fonts and plugin take effect.")
    print("CHUANBAN_RESULT=" + json.dumps(summary_payload, ensure_ascii=False))
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
