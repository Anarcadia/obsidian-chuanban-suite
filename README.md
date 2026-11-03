# chuanban Private Full Suite (船板本地专享与好友完整分享版)

> 👉 **如果你不懂技术或不想手动折腾配置**：请直接打开同目录下的 **[《【必读】给AI助手看的零门槛一键安装引导（AGENT_INSTALL_GUIDE）.md》](【必读】给AI助手看的零门槛一键安装引导（AGENT_INSTALL_GUIDE）.md)**，把里面的一句话口诀复制发给你的 AI 助手（Claude Code / Cursor / Windsurf / Antigravity / Hana / Kimi），AI 会通过内置的 [`install_auto.py`](install_auto.py) 自动为你从 Google Drive 字体共享库拉取字体、配置好全部皮肤和插件！

---

## 📦 完整套件包含内容与云端字体解耦架构

为保持仓库与分享包轻量化合规，字体文件不直接塞入代码库，而是统一托管于独立的 **Google Drive 公开字体共享库**（与 `chuanban-antigravity-theme-patch` 共用同一权威字体网盘源）：

- 🔗 **专属字体 Google Drive 公开下载库**：[https://drive.google.com/drive/folders/1NX92SgVUqtSjWg6bt6sIJXy-cn7J_boC](https://drive.google.com/drive/folders/1NX92SgVUqtSjWg6bt6sIJXy-cn7J_boC)
  - 内含：`AnthropicMono-Regular.ttf`、`AnthropicSans-Regular.ttf`、`AnthropicSans-Bold.ttf`、`AnthropicSerif-Regular.ttf`、`AnthropicSerif-Bold.ttf` 以及 `Sarasa-SuperTTC.ttc`（更纱黑体超集）。
  - *注：运行 `install_auto.py` 时，脚本会自动从该 Google Drive 公开直链下载 5 款 `.ttf` 字体并校验 SHA-256 后安装到系统字库；若网络受限，你或你的 AI 助手也可直接打开上方网盘链接下载。*

```text
chuanban-Obsidian主题与字体排版完整套件（私有分享版）/
├── 【必读】给AI助手看的零门槛一键安装引导（AGENT_INSTALL_GUIDE）.md  # 人类一键复制口诀 + AI 全自动安装与兜底 SOP
├── install_auto.py                     # 跨平台 (macOS/Win/Linux) 自动从网盘拉取字体 + 扫描 Vault 安装激活脚本
├── install.sh                          # macOS/Linux Shell 包装与兜底安装脚本
├── theme/chuanban/                     # 主题本体（绑定 Anthropic Sans/Serif/Mono + 更纱打字机体 + 宋体-简）
│   ├── theme.css
│   └── manifest.json
├── plugins/chuanban-preset-switcher/   # 一键排版预设切换插件（左侧栏书本图标 📖 + Cmd+P 命令面板）
│   ├── main.js
│   └── manifest.json
├── snippets/preset-notion-serif.css    # Notion Desktop 衬线宋体独立 CSS 代码片段
└── config/page-preview.json            # 左侧列表无修饰键悬停直接触发预览卡配置
```

---

## 🚀 两种安装方式

### 方式 A（最省心 · 推荐）：直接交给你的 AI 助手一键全自动安装
复制以下口诀发给你的本地 AI 助手：
```text
请读取《【必读】给AI助手看的零门槛一键安装引导（AGENT_INSTALL_GUIDE）.md》，按里面的 SOP 运行 install_auto.py 帮我从 Google Drive 字体网盘拉取安装全套字体，并自动找到我电脑上的 Obsidian 库，一键安装激活 chuanban 主题和排版切换插件！
```

### 方式 B：一行命令自动拉取网盘字体、扫描本机 Obsidian 库并安装激活
```bash
python3 install_auto.py
```
（脚本会自动从 Google Drive 公开字体库下载安装字体，读取本机 Obsidian 全局注册表，将主题与插件部署进当前打开的 Obsidian 库，并直接合并写入 `appearance.json` 与 `community-plugins.json` 自动启用！）
