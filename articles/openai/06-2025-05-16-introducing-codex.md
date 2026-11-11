---
title_en: Introducing Codex
title_zh: 介绍 Codex
company: openai
date: 2025-05-16
updated: 2025-06-03
url: https://openai.com/index/introducing-codex/
type: summary
category: 编码 Agent
tags:
  - Codex
  - 编码 Agent
  - 沙箱
  - AGENTS.md
  - 长时任务
---

# 介绍 Codex

本文是 OpenAI 于 2025 年 5 月 16 日发布的 Codex 研究预览说明（页面注明该发布帖已过时，请以现行产品文档为准；2025-06-03 更新：ChatGPT Plus 用户可用，并允许任务执行期间访问互联网）。

Codex 是云端软件工程智能体，由面向软件工程优化的 o3 版本 `codex-1` 驱动，可并行处理写功能、修 bug、回答代码库问题并起草 PR。每个任务在预载仓库的隔离云沙箱中运行，可读写文件、执行测试与 linter；完成后提交变更，并以终端日志和测试输出作为可核查证据。仓库中的 `AGENTS.md` 可指导其如何导航、测试与遵守项目规范。发布时强调安全与透明度：需人工审查生成代码；训练上会拒绝恶意软件请求；启动配置在任务执行期间关闭外网，仅与用户提供的代码和预装依赖交互（后续网络选项见官方文档）。同期更新了本地开源的 Codex CLI，并提供更小的 `codex-mini-latest`。官方设想实时结对与异步委派将逐渐融合。
