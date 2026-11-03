const { Plugin, Notice } = require('obsidian');

module.exports = class ChuanbanPresetSwitcherPlugin extends Plugin {
  async onload() {
    this.snippetName = 'preset-notion-serif';

    // 启动时对齐 snippet 状态与 body class，防止三套入口状态分裂
    this.app.workspace.onLayoutReady(() => {
      const active = this.isPresetActive();
      document.body.classList.toggle('preset-notion-serif', active);
    });

    // 1. 在左侧功能区 (Ribbon) 注册一键切换按钮
    this.ribbonIconEl = this.addRibbonIcon('book-open', '一键切换排版预设 (打字机体 ⇄ Notion衬线)', () => {
      this.togglePreset();
    });

    // 2. 注册命令面板动作 (支持在 设置 -> 快捷键 中自由绑定)
    this.addCommand({
      id: 'toggle-typography-preset',
      name: '切换排版预设 (Toggle Preset: Anti打字机体 ⇄ Notion衬线宋体)',
      callback: () => this.togglePreset()
    });
  }

  isPresetActive() {
    const customCss = this.app.customCss;
    let snippetEnabled = false;
    if (customCss && customCss.enabledSnippets) {
      if (customCss.enabledSnippets instanceof Set) {
        snippetEnabled = customCss.enabledSnippets.has(this.snippetName);
      } else if (Array.isArray(customCss.enabledSnippets)) {
        snippetEnabled = customCss.enabledSnippets.includes(this.snippetName);
      }
    }
    return snippetEnabled || document.body.classList.contains('preset-notion-serif');
  }

  async togglePreset() {
    const customCss = this.app.customCss;
    const nextState = !this.isPresetActive();

    // 同步切换 body class 与 snippet 开关，确保任何入口都能一键切回
    document.body.classList.toggle('preset-notion-serif', nextState);
    if (customCss && typeof customCss.setCssEnabledStatus === 'function') {
      customCss.setCssEnabledStatus(this.snippetName, nextState);
    }

    if (nextState) {
      new Notice('🖋️ 已切换为：Notion 衬线宋体预设\n(西文无衬线 + 全角宋体-简 · 1.68行高 · 0.82em/1.05em段距)', 3200);
    } else {
      new Notice('⌨️ 已切换为：Anti 更纱打字机体预设\n(Sarasa Mono Slab SC · 1.78行高 · 0.38em/0.95em段距 · 0.25px润墨)', 3200);
    }
  }
};
