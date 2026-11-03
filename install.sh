#!/usr/bin/env bash
set -euo pipefail

# ==============================================================================
# chuanban Private Full Suite — POSIX Installer Wrapper & Fallback (macOS / Linux)
# Prefers install_auto.py for automatic Google Drive font pull & non-destructive
# JSON merging; falls back to POSIX curl + file deployment if Python 3 is unavailable.
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GDRIVE_FONT_URL="https://drive.google.com/drive/folders/1NX92SgVUqtSjWg6bt6sIJXy-cn7J_boC"

if command -v python3 >/dev/null 2>&1; then
  # On macOS, ensure /usr/bin/python3 is not an uninitialized Xcode CLT stub
  if [ "$(uname -s)" != "Darwin" ] || xcode-select -p >/dev/null 2>&1 || [ "$(command -v python3)" != "/usr/bin/python3" ]; then
    exec python3 "$SCRIPT_DIR/install_auto.py" "$@"
  fi
fi

if [ $# -lt 1 ]; then
  echo "Usage: ./install.sh <path-to-obsidian-vault>"
  echo "Example: ./install.sh ~/Documents/MyVault"
  exit 1
fi

VAULT_PATH="$1"
if [ ! -d "$VAULT_PATH/.obsidian" ]; then
  echo "[ERROR] '$VAULT_PATH/.obsidian' not found. Please specify a valid Obsidian vault root."
  exit 1
fi

# 1. Install Anthropic Fonts (from local ./fonts if pre-downloaded, or pull from Google Drive)
if [ "$(uname -s)" = "Darwin" ]; then
  FONT_DEST="$HOME/Library/Fonts"
else
  FONT_DEST="$HOME/.local/share/fonts"
fi
mkdir -p "$FONT_DEST"

if [ -d "$SCRIPT_DIR/fonts" ] && ls "$SCRIPT_DIR/fonts/"*.ttf >/dev/null 2>&1; then
  cp -f "$SCRIPT_DIR/fonts/"*.ttf "$FONT_DEST/"
  echo "[OK] Installed pre-downloaded Anthropic (.ttf) fonts -> $FONT_DEST"
elif command -v curl >/dev/null 2>&1; then
  echo "[INFO] Pulling Anthropic (.ttf) fonts from Google Drive ($GDRIVE_FONT_URL)..."
  curl -fsSL "https://drive.google.com/uc?export=download&id=1NK_1Q2MBl5yHw94pC_kbzybDgqEFCZVk" -o "$FONT_DEST/AnthropicMono-Regular.ttf" || echo "[WARN] Please download AnthropicMono-Regular.ttf manually from $GDRIVE_FONT_URL"
  curl -fsSL "https://drive.google.com/uc?export=download&id=1IwmkmuLNmHrqq6jAQxso46FXN9XgDAVo" -o "$FONT_DEST/AnthropicSans-Regular.ttf" || echo "[WARN] Please download AnthropicSans-Regular.ttf manually from $GDRIVE_FONT_URL"
  curl -fsSL "https://drive.google.com/uc?export=download&id=1VyJi_4qCy2DrZvo_V_ShpUrbHbjL1MwG" -o "$FONT_DEST/AnthropicSans-Bold.ttf" || echo "[WARN] Please download AnthropicSans-Bold.ttf manually from $GDRIVE_FONT_URL"
  curl -fsSL "https://drive.google.com/uc?export=download&id=1RZ1rMYYFlr5B-slSSZV-DCJtv5AfTMUV" -o "$FONT_DEST/AnthropicSerif-Regular.ttf" || echo "[WARN] Please download AnthropicSerif-Regular.ttf manually from $GDRIVE_FONT_URL"
  curl -fsSL "https://drive.google.com/uc?export=download&id=1-LJfTa1wasIqkoCCHI4mfVyh8tzreiAO" -o "$FONT_DEST/AnthropicSerif-Bold.ttf" || echo "[WARN] Please download AnthropicSerif-Bold.ttf manually from $GDRIVE_FONT_URL"
else
  echo "[WARN] Please download the fonts from Google Drive: $GDRIVE_FONT_URL -> $FONT_DEST"
fi

if command -v fc-cache >/dev/null 2>&1; then
  fc-cache -f "$FONT_DEST" >/dev/null 2>&1 || true
fi

# 2. Install Theme (chuanban Private Edition)
mkdir -p "$VAULT_PATH/.obsidian/themes/chuanban"
cp -f "$SCRIPT_DIR/theme/chuanban/theme.css" "$VAULT_PATH/.obsidian/themes/chuanban/theme.css"
cp -f "$SCRIPT_DIR/theme/chuanban/manifest.json" "$VAULT_PATH/.obsidian/themes/chuanban/manifest.json"
echo "[OK] Installed chuanban theme -> $VAULT_PATH/.obsidian/themes/chuanban"

# 3. Install Typography Preset Switcher Plugin
mkdir -p "$VAULT_PATH/.obsidian/plugins/chuanban-preset-switcher"
cp -f "$SCRIPT_DIR/plugins/chuanban-preset-switcher/main.js" "$VAULT_PATH/.obsidian/plugins/chuanban-preset-switcher/main.js"
cp -f "$SCRIPT_DIR/plugins/chuanban-preset-switcher/manifest.json" "$VAULT_PATH/.obsidian/plugins/chuanban-preset-switcher/manifest.json"
echo "[OK] Installed plugin '排版预设切换器 (Chuanban Preset Switcher)' -> $VAULT_PATH/.obsidian/plugins/chuanban-preset-switcher"

# 4. Install Companion CSS Snippet
mkdir -p "$VAULT_PATH/.obsidian/snippets"
cp -f "$SCRIPT_DIR/snippets/preset-notion-serif.css" "$VAULT_PATH/.obsidian/snippets/preset-notion-serif.css"
echo "[OK] Installed preset-notion-serif.css snippet -> $VAULT_PATH/.obsidian/snippets/"

# 5. Install Page Preview Hover Configuration (with backup)
TS="$(date +%Y%m%d-%H%M%S)"
if [ -f "$VAULT_PATH/.obsidian/page-preview.json" ]; then
  cp -f "$VAULT_PATH/.obsidian/page-preview.json" "$VAULT_PATH/.obsidian/page-preview.json.$TS.bak"
fi
cp -f "$SCRIPT_DIR/config/page-preview.json" "$VAULT_PATH/.obsidian/page-preview.json"
echo "[OK] Configured sidebar hover preview -> $VAULT_PATH/.obsidian/page-preview.json"

echo ""
echo "[SUCCESS] Files deployed! If JSON configs were not auto-merged (no Python 3), please merge appearance.json & community-plugins.json per AGENT_INSTALL_GUIDE.md §3."
