---
title_en: Building a C compiler with a team of parallel Claudes
title_zh: 用一组并行的 Claude 构建 C 编译器
company: anthropic
date: 2026-02-05
url: https://www.anthropic.com/research/building-c-compiler
type: summary
category: 编码 Agent
tags:
  - Claude Code
  - 多 Agent
  - 编码 Agent
  - 并行
---

# 用一组并行的 Claude 构建 C 编译器

Safeguards 团队研究员 Nicholas Carlini 介绍了一种称为 “agent teams” 的监督方法：多个 Claude 实例在共享代码库上并行工作，无需持续人工干预。为做压力测试，他让 16 个智能体从零编写基于 Rust 的 C 编译器，目标是能够编译 Linux 内核。在近 2,000 个 Claude Code sessions 和约 20,000 美元 API 成本后，团队产出了约 10 万行编译器，可以在 x86、ARM 和 RISC-V 上构建 Linux 6.9。编译器开源见 [anthropics/claudes-c-compiler](https://github.com/anthropics/claudes-c-compiler)。

Harness 是一个简单循环（类似 Ralph-loop）：智能体完成一项任务后立即接下一项，并以 `--dangerously-skip-permissions` 在容器中运行。并行可以同时调试多个问题，并允许角色专门化。作者强调：测试必须极高质量，否则智能体会解决错误问题；要把测试和反馈写给“刚刚掉进全新容器、没有任何 context 的 Claude”，而不是写给自己；用 README、进度文件、锁和 CI 让多个智能体能自行定向并避免互相破坏已有功能。早期原型没有编排智能体，由每个 Claude 自行决定下一步。文章也讨论了该方法的上限与评估。
