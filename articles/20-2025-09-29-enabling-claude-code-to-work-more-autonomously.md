# 让 Claude Code 更能自主工作

- 英文标题：Enabling Claude Code to work more autonomously
- 中文标题：让 Claude Code 更能自主工作
- 发布日期：2025-09-29
- 原文链接：https://www.anthropic.com/news/enabling-claude-code-to-work-more-autonomously
- 翻译类型：中文摘要

---

这是一则产品新闻，介绍由 Claude Sonnet 4.5 驱动的若干 Claude Code 升级，使其能在终端和 IDE 中处理更长、更复杂的开发任务：

- **原生 VS Code 扩展**（当时为 beta）：在 IDE 侧边栏中实时查看 Claude 的改动和 inline diffs。
- **终端界面 2.0**：改进状态可见性，并可用 Ctrl+r 搜索 prompt 历史。
- **Claude Agent SDK**（原 Claude Code SDK）：开放与 Claude Code 相同的核心工具、context 管理和权限框架，并支持 subagents 和 hooks。
- **Checkpoints**：在每次改动前自动保存代码状态，可通过连按 Esc 或 `/rewind` 回退。可以选择恢复代码、对话或两者。Checkpoints 适用于 Claude 的编辑，不适用于用户编辑或 bash 命令，建议与版本控制一起使用。
- 与 **subagents、hooks 和后台任务** 结合，更适合委托复杂、探索性工作，同时保持控制。
