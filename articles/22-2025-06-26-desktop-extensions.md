# Desktop Extensions：为 Claude Desktop 一键安装 MCP server

- 英文标题：Desktop Extensions: One-click MCP server installation for Claude Desktop
- 中文标题：Desktop Extensions：为 Claude Desktop 一键安装 MCP server
- 发布日期：2025-06-26
- 更新日期：2025-09-11（文件扩展名由 .dxt 改为 .mcpb）
- 原文链接：https://www.anthropic.com/research/desktop-extensions
- 翻译类型：中文摘要

---

MCP 发布后，开发者为 Claude Desktop 构建了大量本地 MCP servers，但安装门槛很高：需要开发者工具、手动编辑 JSON 配置、处理依赖冲突、缺少发现机制，更新也要手动重装。非技术用户很难用上这些能力。

本文介绍 Desktop Extensions：把整个本地 MCP server（含依赖）打包成一个可安装包。用户只需下载文件、双击用 Claude Desktop 打开并点击 “Install”，无需终端或手工配置。扩展本质是一个 zip 归档，内含 `manifest.json` 与 server 实现。

2025 年 9 月 11 日更新：文件扩展名从 `.dxt` 改为 `.mcpb`（MCP Bundle）。已有 `.dxt` 扩展仍可用，新扩展建议使用 `.mcpb`；功能不变，只是命名约定更新。
