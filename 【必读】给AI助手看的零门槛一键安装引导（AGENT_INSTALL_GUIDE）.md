# 【必读】chuanban 主题与双字体排版套件 — 萌新 & AI 助手零门槛一键安装引导 (v1.2 云端字体解耦 & Opus 核验加固版)

> **写给收到这份分享包的你（完全不需要懂技术！）**：
> 你**不需要**自己去找 `.obsidian` 隐藏文件夹，也**不需要**自己敲命令或进设置里翻找开关。
> 只要你电脑上有任何一款能操作本地文件的 **AI 助手**（如 **Claude Code、Cursor、Windsurf、Antigravity、Codex、Hana、Kimi CLI** 等），把解压后的这个文件夹路径发给它，再复制下面这段**【一键安装口诀】**发给它，你的 AI 助手就会自动读完本文档，完成**环境探测 → 从 Google Drive 字体共享网盘自动下载安装字体 → 自动部署主题与插件（含无 Python 手工兜底）→ 8 项状态自检**，帮你把**全套字体、chuanban 皮肤、左侧栏一键字体切换插件、悬停高密度预览卡**全部装好并激活！

---

## 🪄 第一部分：复制发给你的 AI 助手的一键安装口诀（人类用户只需做这一步）

把下面框里的话复制发给你的 AI 助手即可（如果压缩包还没解压，可以把压缩包直接拖进聊天框）：

```text
我收到了朋友分享的「chuanban Obsidian 主题与双字体排版完整套件」（包含主题、一键切换字体插件和配置文件，配套专属字体托管在 Google Drive 公开网盘）。
请你先解压（如果是 zip 包）并完整阅读里面的《【必读】给AI助手看的零门槛一键安装引导（AGENT_INSTALL_GUIDE）.md》，严格按照里面的「AI Agent 全自动安装、网盘字体拉取、异常兜底与 8 项状态核验 SOP」执行：
1. 先探测我电脑上的 Obsidian 库，并从文档指定的 Google Drive 字体共享网盘自动下载安装全套字体，帮我把 chuanban 主题、排版预设切换器插件和预览卡配置全部非破坏性安装并激活；
2. 如果自动脚本或网盘直连因环境原因受阻，请立即自动切换文档 §2/§3 的「Agent 兜底方案」完成部署，不要让我手动折腾；
3. 跑完 §4 的「8 项状态核验清单」确认无误后，再告诉我要怎么使用。
```

---

## 🔗 配套专属字体 Google Drive 公开共享网盘（与项目代码解耦）

本套件不在代码仓库或安装包内直接捆绑字体二进制文件，所有配套字体均托管于独立的 **Google Drive 公开共享文件夹**（免登录直接访问）：

- **📁 字体网盘总目录（人类浏览 / Agent 浏览器访问）**：
  **[https://drive.google.com/drive/folders/1NX92SgVUqtSjWg6bt6sIJXy-cn7J_boC](https://drive.google.com/drive/folders/1NX92SgVUqtSjWg6bt6sIJXy-cn7J_boC)**
- **⬇️ 单文件免登录直链（供 `install_auto.py` 或 Agent 通过 `curl -L` 直接拉取，均含 SHA-256 校验）**：
  1. `AnthropicMono-Regular.ttf` (`149,556 B`, SHA256: `0e686e9d651bf3b7448bbc7ec5c5ffd48e3ae9b07710d26ed332170487f60295`)
     `https://drive.google.com/uc?export=download&id=1NK_1Q2MBl5yHw94pC_kbzybDgqEFCZVk`
  2. `AnthropicSans-Regular.ttf` (`310,084 B`, SHA256: `6b95f2701784e79c30334668c85077c187c66ef0e0b105647a27c253ff41fb32`)
     `https://drive.google.com/uc?export=download&id=1IwmkmuLNmHrqq6jAQxso46FXN9XgDAVo`
  3. `AnthropicSans-Bold.ttf` (`310,084 B`, SHA256: `a79cf47de0f8e8165e048e742d97c5ec9488e09d7af5ddde20efdbfb75a4993b`)
     `https://drive.google.com/uc?export=download&id=1VyJi_4qCy2DrZvo_V_ShpUrbHbjL1MwG`
  4. `AnthropicSerif-Regular.ttf` (`510,352 B`, SHA256: `5806e7fbfebfe6683fdb2c16d8eb91b98ccd6b4ba0d477e8f5167782e0d7b009`)
     `https://drive.google.com/uc?export=download&id=1RZ1rMYYFlr5B-slSSZV-DCJtv5AfTMUV`
  5. `AnthropicSerif-Bold.ttf` (`510,352 B`, SHA256: `3e0d9660390f1800f229e2724cf0b09030ec53188cd3d361ca210077ce564426`)
     `https://drive.google.com/uc?export=download&id=1-LJfTa1wasIqkoCCHI4mfVyh8tzreiAO`
  *(此外该网盘目录内还提供 `Sarasa-SuperTTC.ttc` 更纱黑体超集包，亦可按需下载或通过 `brew install --cask font-sarasa-gothic` 安装)*。

---

## 🤖 第二部分：AI Agent 全自动安装、异常兜底与状态核验 SOP（供 AI 助手阅读并严格执行）

你好，AI Agent！当用户将本套件交给你时，说明用户希望**零手动配置、且绝不破坏原有插件与设置**地在他的 Obsidian 中用上全套 `chuanban` 主题与配套插件。请严格按以下 **§0 → §1 → §2（如遇错）→ §3（无 Python 兜底）→ §4（必做核验）** 顺序执行：

---

### §0 安装前安全约定与库范围确认（Pre-Flight Safety Contract）

1. **备份与非破坏性铁律**：
   - 无论通过脚本还是手工修改 `<Vault>/.obsidian/` 下的 JSON 配置文件（`appearance.json`、`community-plugins.json`、`page-preview.json`），**必须在修改前生成带时间戳的 `.bak` 备份文件**。
   - **严禁清空或重置用户原有的 `community-plugins.json`！** 如果某个 JSON 文件解析失败（如语法损坏），必须立即中止对该文件的写入并报告给用户，**绝不允许用空数组 `[]` 或空对象 `{}` 覆盖用户原有配置**。
2. **检测 Obsidian 是否正在运行**：
   - Obsidian 在运行期间可能会在退出时将内存中的旧配置回写覆盖磁盘，且新安装的系统级字体必须**完全退出并重启 Obsidian**（仅按 `Cmd+R` 无法刷新 Chromium 底层系统字库缓存）才能生效。
   - 如果检测到 Obsidian 正在运行，请提醒用户在安装完成后**完全退出并重新打开 Obsidian**。
3. **多库智能保护约定**：
   - `install_auto.py` 默认优先只装当前正在打开（`open: true`）的活跃库，自动跳过已关闭的其他专有库以保护它们各自的独立主题；如需安装到全部库可加 `--all`，或先跑 `--list` 列出所有库询问用户。

---

### §1 跨平台 Python 解释器探测与 `install_auto.py` 自动执行协议

本套件根目录内置了经过跨平台加固的零依赖安装脚本 [`install_auto.py`](install_auto.py)（内置从 Google Drive 自动拉取上述 5 款 `.ttf` 字体并校验 SHA-256 的逻辑）。在调用它之前，请**先探测当前操作系统下真正可用的 Python 3 解释器**（切勿盲目裸跑 `python3`）：

#### 1.1 各平台 Python 解释器安全探测顺序
- **macOS**：
  1. 先执行 `xcode-select -p >/dev/null 2>&1` 或检查 `which python3`。如果本机只有 `/usr/bin/python3` 且未安装 Xcode Command Line Tools，直接调用 `/usr/bin/python3` 会弹出系统安装弹窗并阻塞卡死！此时若无 Homebrew Python（`/opt/homebrew/bin/python3`），请**直接跳过脚本，走下方 §3 手工兜底协议**。
- **Windows (PowerShell / CMD)**：
  1. Windows 下通常没有 `python3` 命令，或者 `python3.exe` 指向 `Microsoft\WindowsApps\python3.exe`（微软商店假别名，运行会返回退出码 `9009` 或弹出微软商店窗口）。
  2. 请先用 `where.exe py` 或 `where.exe python` 检查：若路径不含 `WindowsApps`，优先使用 `py -3` 或 `python`；并在执行前设置环境变量 `$env:PYTHONUTF8="1"`。
  3. 若本机未安装真正的 Python，请**直接跳过脚本，走下方 §3 手工兜底协议**。
- **Linux**：
  1. 检查 `python3 --version`（要求 Python ≥ 3.7）。

#### 1.2 执行自动安装并读取机器状态契约 `CHUANBAN_RESULT`

```bash
# 1. 可选：先列出本机发现的所有 Obsidian 库
python3 "<套件目录>/install_auto.py" --list

# 2. 执行全自动安装（自动从 Google Drive 拉取字体 + 配置当前打开的库；传 --all 可配置所有库）
python3 "<套件目录>/install_auto.py"
```

**Agent 必须检查脚本输出的最后一行 `CHUANBAN_RESULT={...}` 以及进程退出码**：
- **退出码 `0` 且 `"status": "ok"`**：所有目标库与云端字体均下载、安装并校验成功，进入 **§4** 做最终核验。
- **退出码 `2` 且 `"status": "partial"`**：
  - 若 `"fonts": "manual_download_needed"`：说明当前终端无法直连 Google Drive（例如终端未配置代理）。此时主题与插件**已经安装成功**！请你尝试用你的浏览器工具或本地代理端口拉取上方 5 条 Google Drive 字体直链放入系统字体目录，或者把网盘链接 `https://drive.google.com/drive/folders/1NX92SgVUqtSjWg6bt6sIJXy-cn7J_boC` 发给用户请他点击下载放到 `<套件目录>/fonts/` 后重跑一次 `install_auto.py`。
- **退出码 `1` 或非零异常**：脚本未能完成安装，请立即对照 **§2 诊断表** 排查，或直接切换 **§3 手工兜底协议**！

---

### §2 脚本异常与失败状态诊断对照表（Agent 状态感知表）

当 `install_auto.py` 退出码非 `0` 或输出错误时，请按此表秒级定位并自动接管处理：

| 脚本现象 / 退出码 / 错误关键词 | 根本原因 | Agent 自动接管与兜底动作 |
| :--- | :--- | :--- |
| **`"fonts": "manual_download_needed"`** | 终端未走代理，无法直连 `drive.google.com` | 探测本机常见代理端口（如 `http://127.0.0.1:7890`）设置 `HTTPS_PROXY` 重跑；若无代理，引导用户打开 [Google Drive 字体网盘](https://drive.google.com/drive/folders/1NX92SgVUqtSjWg6bt6sIJXy-cn7J_boC) 下载 `.ttf` 放入 `<套件目录>/fonts/` 后重跑 |
| **退出码 `9009`** / 弹出微软商店 / `command not found: python3` | Windows 命中 `WindowsApps` 假别名，或本机未安装 Python | 改试 `py -3 "<套件目录>/install_auto.py"`；若仍无 Python，**立即切换 §3 使用 Agent 原生工具手工部署** |
| **`UnicodeEncodeError`** | Windows 终端管道代码页（GBK/cp1252）编码冲突 | 先设置环境变量 `PYTHONUTF8=1`（PowerShell: `$env:PYTHONUTF8="1"`）后重跑，或走 **§3** |
| **`"reason": "no_vaults_found"`** / `No Obsidian vaults auto-discovered` | 用户库未登记在标准 `obsidian.json`（如绿色版、外置盘）或受 macOS TCC 权限拦截 | 用你的文件搜索工具搜索本机含 `.obsidian` 的目录（如 `~/Documents`、桌面、iCloud Drive `~/Library/Mobile Documents/iCloud~md~obsidian/Documents`），找到路径后显式传参：`python3 install_auto.py "/找到的/库路径"` |
| **`Malformed JSON in ... (backed up to ...bak)`** (`ConfigParseError`) | 用户原有的 `appearance.json` 或 `community-plugins.json` 含语法错误（如手改多写了尾随逗号） | 脚本已保护性中止并生成 `.bak`。请用你的 Read 工具读取该损坏的 JSON 文件，帮用户修复 JSON 语法错误（绝对保留原有内容），再重新运行脚本 |
| **`PermissionError`**（复制字体时） | Obsidian 或系统正在占用同名 `.ttf` 字体文件 | 若目标字体文件已存在且大小 > 0，说明字体本就已安装，可忽略该警告继续配置库；否则请用户先关闭 Obsidian 后重跑 |
| **`"restricted_mode_suspected": true`** | 该库此前从未开启过第三方插件（处于 Obsidian 安全模式） | 文件与配置均已就绪！必须在汇报时重点提醒用户：`设置 -> 第三方插件 -> 关闭安全模式（Turn on community plugins）` |

---

### §3 不依赖 Python 的 Agent 原生工具 / Shell / PowerShell 纯手工兜底协议

**如果用户电脑没有可用的 Python 环境，或者 `install_auto.py` 因任何原因无法运行，请你直接用你自带的文件读写工具（Read / Write / Edit）或系统 Shell / PowerShell 按以下 4 步手工完成部署（绝不要让人类用户自己动手）**：

#### 兜底 Step A：定位用户的 Obsidian 库路径（`<Vault>`）
读取以下全局注册表文件获取 `"path"` 字段（若不存在则搜索本机 `.obsidian` 文件夹）：
- **macOS**：`~/Library/Application Support/obsidian/obsidian.json`
- **Windows**：`%APPDATA%\obsidian\obsidian.json`
- **Linux**：`~/.config/obsidian/obsidian.json`（或 Flatpak `~/.var/app/md.obsidian.Obsidian/config/obsidian/obsidian.json`、Snap `~/snap/obsidian/current/.config/obsidian/obsidian.json`）

#### 兜底 Step B：从 Google Drive 网盘下载并注册 5 款 `.ttf` 字体
- 先使用 `curl -fsSL`（或 PowerShell `Invoke-WebRequest`）从本文档顶部的 **5 条 Google Drive 单文件免登录直链**将 `.ttf` 下载到系统用户字体目录（若用户已手动从 `https://drive.google.com/drive/folders/1NX92SgVUqtSjWg6bt6sIJXy-cn7J_boC` 下载到 `<套件目录>/fonts/` 或 `~/Downloads/`，则直接复制）：
  - **macOS 目标目录**：`~/Library/Fonts/`
  - **Linux 目标目录**：`~/.local/share/fonts/`（复制后运行 `fc-cache -f ~/.local/share/fonts/`）
  - **Windows (PowerShell) 目标目录与注册表写入**：**注意！Windows 用户级字体目录必须同时写入 `HKCU` 注册表，否则 Chromium/Obsidian 无法识别字体！** 请在 PowerShell 中执行：
    ```powershell
    $dst = "$env:LOCALAPPDATA\Microsoft\Windows\Fonts"
    New-Item -ItemType Directory -Force $dst | Out-Null
    $reg = 'HKCU:\Software\Microsoft\Windows NT\CurrentVersion\Fonts'
    $fonts = @{
      "AnthropicMono-Regular.ttf"  = "1NK_1Q2MBl5yHw94pC_kbzybDgqEFCZVk"
      "AnthropicSans-Regular.ttf"  = "1IwmkmuLNmHrqq6jAQxso46FXN9XgDAVo"
      "AnthropicSans-Bold.ttf"     = "1VyJi_4qCy2DrZvo_V_ShpUrbHbjL1MwG"
      "AnthropicSerif-Regular.ttf" = "1RZ1rMYYFlr5B-slSSZV-DCJtv5AfTMUV"
      "AnthropicSerif-Bold.ttf"    = "1-LJfTa1wasIqkoCCHI4mfVyh8tzreiAO"
    }
    foreach ($kv in $fonts.GetEnumerator()) {
      $target = Join-Path $dst $kv.Key
      Invoke-WebRequest -Uri "https://drive.google.com/uc?export=download&id=$($kv.Value)" -OutFile $target
      $base = [System.IO.Path]::GetFileNameWithoutExtension($kv.Key)
      New-ItemProperty -Path $reg -Name "$base (TrueType)" -Value $target -PropertyType String -Force | Out-Null
    }
    ```

#### 兜底 Step C：复制 5 个核心主题、插件与片段文件到 `<Vault>/.obsidian/`
请创建对应子目录并复制以下 5 个文件：
1. `<套件目录>/theme/chuanban/theme.css` → `<Vault>/.obsidian/themes/chuanban/theme.css`
2. `<套件目录>/theme/chuanban/manifest.json` → `<Vault>/.obsidian/themes/chuanban/manifest.json`
3. `<套件目录>/plugins/chuanban-preset-switcher/main.js` → `<Vault>/.obsidian/plugins/chuanban-preset-switcher/main.js`
4. `<套件目录>/plugins/chuanban-preset-switcher/manifest.json` → `<Vault>/.obsidian/plugins/chuanban-preset-switcher/manifest.json`
5. `<套件目录>/snippets/preset-notion-serif.css` → `<Vault>/.obsidian/snippets/preset-notion-serif.css`

#### 兜底 Step D：使用你自带的 Read/Write 工具安全合并 3 个 JSON 配置文件
> ⚠️ **严厉警告（特别是 Windows PowerShell 5.1 环境）**：
> 1. **优先使用你作为 AI Agent 自带的 `Read` / `Edit` / `Write` 文件工具**直接读取和修改以下 JSON 文件，避免用 PowerShell 处理 JSON！
> 2. 如果万不得已必须在 PowerShell 5.1 中写文件，**绝对禁止使用 `Set-Content -Encoding UTF8`**（PowerShell 5.1 会写入 UTF-8 BOM 头，导致某些工具解析异常），必须使用 `[System.IO.File]::WriteAllText($path, $jsonStr, (New-Object System.Text.UTF8Encoding $false))`；且 PowerShell 的 `ConvertTo-Json` 遇到单元素数组会将其展开成字符串，必须写 `ConvertTo-Json -InputObject @($list)`！

请对每个目标 `<Vault>/.obsidian/` 下的 3 个 JSON 文件先备份为 `.bak`，再按以下规则**非破坏性合并**：
1. **`<Vault>/.obsidian/appearance.json`**（对象 `{}`）：
   - 保留用户原有的所有键值（如 `baseFontSize`、`theme`、`enabledCssSnippets` 等）；
   - 设置 `"cssTheme": "chuanban"`；
   - 若不存在 `"showRibbon"` 键，则设置 `"showRibbon": true`。
2. **`<Vault>/.obsidian/community-plugins.json`**（字符串数组 `[]`）：
   - **完整保留数组中已有的所有插件 ID**（如 `"dataview"`, `"templater-obsidian"` 等，一个都不许少！）；
   - 若数组中还没有 `"chuanban-preset-switcher"`，将其追加到数组末尾。
3. **`<Vault>/.obsidian/page-preview.json`**（对象 `{}`）：
   - 保留用户原有的其他键，将 `<套件目录>/config/page-preview.json` 中的键值合并进去（使左侧文件树支持免按修饰键直接悬停预览）。

---

### §4 安装后 Agent 必做的 8 项状态核验清单（Post-Install Verification Checklist）

**在向用户说“已经安装成功”之前，你必须亲自执行以下核验（可直接运行 `python3 "<套件目录>/install_auto.py" --verify` 并配合检查）**：

- [ ] **核验 1（5 大核心文件落盘）**：确认目标库 `<Vault>/.obsidian/` 下以下 5 个文件全部存在且文件大小 > 0：
  - `themes/chuanban/theme.css`、`themes/chuanban/manifest.json`
  - `plugins/chuanban-preset-switcher/main.js`、`plugins/chuanban-preset-switcher/manifest.json`
  - `snippets/preset-notion-serif.css`
- [ ] **核验 2（主题已激活且 JSON 合法）**：读取 `<Vault>/.obsidian/appearance.json`，确认 JSON 格式合法且 `"cssTheme": "chuanban"`。
- [ ] **核验 3（插件列表超集保护）**：读取 `<Vault>/.obsidian/community-plugins.json`，确认包含 `"chuanban-preset-switcher"`，且对比备份文件 `.bak` 确认**用户原有的其他社区插件一个都没有丢失**。
- [ ] **核验 4（Google Drive 字体下载与系统可见性）**：
  - macOS：确认 `~/Library/Fonts/AnthropicSans-Regular.ttf` 等 5 个文件已存在；
  - Windows：确认 `$env:LOCALAPPDATA\Microsoft\Windows\Fonts\Anthropic*.ttf` 已存在且 `HKCU:\Software\Microsoft\Windows NT\CurrentVersion\Fonts` 中含有对应键值；
  - Linux：确认 `~/.local/share/fonts/Anthropic*.ttf` 已存在。
- [ ] **核验 5（可选更纱黑体检查与询问）**：
  - 检查本机是否已安装开源字体 `Sarasa Mono Slab SC`（更纱黑体 Slab）。
  - 若未安装：可引导用户从同一个 [Google Drive 字体共享库](https://drive.google.com/drive/folders/1NX92SgVUqtSjWg6bt6sIJXy-cn7J_boC) 下载 `Sarasa-SuperTTC.ttc` 双击安装，或在 macOS 上先征得用户同意后执行 `brew install --cask font-sarasa-gothic`。
- [ ] **核验 6（提醒用户完全重启 Obsidian）**：明确告知用户：**如果刚才安装时 Obsidian 处于打开状态，请务必先按 `Cmd+Q`（macOS）或 `Alt+F4`（Windows）完全退出并重新打开 Obsidian**，让新安装的字体和配置彻底生效（切勿在重启前改动 Obsidian 外观设置以免内存旧状态回写）。
- [ ] **核验 7（安全模式解锁提示）**：如果 `CHUANBAN_RESULT` 报告 `"restricted_mode_suspected": true`（或安装前 `community-plugins.json` 为空），必须提醒用户：打开 Obsidian `设置 -> 第三方插件 -> 点击「关闭安全模式 (Turn on community plugins)」`，确保插件 **`排版预设切换器 (Chuanban Preset Switcher)`** 处于开启状态。
- [ ] **核验 8（交付 30 秒使用指南）**：全部核验通过后，向用户展示以下 3 条简明使用说明：
  1. **📖 一键切换两套字体预设**：点击 Obsidian **最左侧功能栏（Ribbon）上的「书本图标 📖」**（或按 `Cmd/Ctrl + P` 搜索 `切换排版预设`），即可在 **「Anti 更纱打字机体（1.78行高 · 活字感）」** 与 **「Notion 衬线宋体（Anthropic Sans + 全角宋体 · 1.68行高）」** 之间秒级无缝切换！
  2. **🔍 左侧目录丝滑悬停预览卡**：鼠标直接悬停在左侧文件列表的任意文章标题上（**无需按住 `Cmd/Ctrl` 键**），即可立刻弹出固定 `13px` 高信息密度的文章预览卡，且已自动隐藏顶部的 YAML 属性框，一眼看到正文干货。
  3. **🎨 温暖护眼的象牙与燕麦纸感**：主阅读区采用微暖亮白象牙纸底（`#FCFCFB`），侧边栏采用暖燕麦色（`#F7F5F0`），搭配陶土砖红强调色（`#D97757`）、柔和草绿文字圈选与淡暖黄高亮，长篇码字或深度阅读久看不累。
