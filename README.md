# OSS Bounty Scope

这是一个自动维护的开源赏金项目 (Bug Bounty) 目标列表。它整合了各大平台的公开数据，并支持手动补充核心基础设施、AI 及 Web3 项目。

## 🚀 项目功能

- **多平台聚合**：自动从 [bounty-targets-data](https://github.com/arkadiyt/bounty-targets-data) 提取 HackerOne, Bugcrowd, YesWeHack, Intigriti 等平台的开源项目。
- **核心补充**：手动维护 `manual_additions.txt`，包含 IBB (Internet Bug Bounty), Google, Microsoft, Meta, Vercel 以及热门 AI/Web3 核心仓库。
- **自动同步**：通过 GitHub Actions 每天自动更新上游数据并重新生成列表。
- **纯净输出**：生成的 `oss_repos_only.txt` 仅包含去重后的仓库 URL，方便直接导入扫描工具。

## 📂 文件说明

- `oss_repos_only.txt`: **最终产物**，包含所有去重后的开源仓库 URL。
- `oss_bounty_targets.txt`: 详细列表，包含所属平台、程序名称及对应的仓库。
- `manual_additions.txt`: 手动维护的项目清单，按赏金来源分类。
- `extract_oss_bounty.py`: 提取与合并的核心脚本。

## 🛠️ 如何添加新目标

如果你发现新的开源赏金项目，只需修改 `manual_additions.txt`：

1. 打开 `manual_additions.txt`。
2. 在合适的分类下添加仓库 URL（例如 `https://github.com/owner/repo`）。
3. 提交并 Push 代码。

GitHub Actions 将在下次运行时自动将其合并到最终列表。

## 🤖 自动化机制

本项目配置了 GitHub Actions (`.github/workflows/sync-upstream.yml`):
- **定时更新**：每天 UTC 0:00 自动运行。
- **手动触发**：在 GitHub Actions 页面手动运行 "Sync Upstream"。

## ⚖️ 声明

本项目仅用于安全研究。在进行任何渗透测试前，请务必阅读并遵守各项目官方的 **Vulnerability Reward Program (VRP)** 政策及范围。
