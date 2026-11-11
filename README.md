# Anthropic Agent 开发文章整理（附中文翻译）

本仓库按**发表时间从新到旧**整理 Anthropic 已公开发表、与 Agent 开发相关的工程 / 研究 / 部分产品文章，并附中文译本或摘要。

主题包括：构建智能体、agent harness、工具设计、context engineering、智能体评估（evals）、Claude Agent SDK、Claude Code 工程实践、多智能体系统、记忆（memory）、Managed Agents、长时运行智能体等。

共收录 **26** 篇（均已对照官方页面核实，未编造篇目）：其中 **17** 篇为全文翻译，**9** 篇为中文摘要（因篇幅较大，优先完整翻译最核心的约 15–20 篇，其余以摘要收录，类型见下表与各文件页眉）。时间范围覆盖 **2024-12 至 2026-11**。

也可阅读合集网页：[anthropic-agent-articles-zh.html](anthropic-agent-articles-zh.html)（同样按时间从新到旧排列，目录与标题中均标明发表日期）。

单篇文章位于 [`articles/`](articles/) 目录，文件名以序号开头，使列表按从新到旧排序。

## 文章目录（按发表时间，从新到旧）

| 日期 | 标题（英） | 中文标题 | 类型 | 原文 | 译文链接 |
| --- | --- | --- | --- | --- | --- |
| 2026-11-06 | The components of agent memory | 智能体记忆的组成 | 全文翻译 | [原文](https://www.anthropic.com/research/components-of-agent-memory) | [01-2026-11-06-the-components-of-agent-memory.md](articles/01-2026-11-06-the-components-of-agent-memory.md) |
| 2026-05-25 | How we contain Claude across products | 我们如何在各产品中约束 Claude | 中文摘要 | [原文](https://www.anthropic.com/research/how-we-contain-claude) | [02-2026-05-25-how-we-contain-claude.md](articles/02-2026-05-25-how-we-contain-claude.md) |
| 2026-04-23 | An update on recent Claude Code quality reports | 关于近期 Claude Code 质量报告的更新 | 中文摘要 | [原文](https://www.anthropic.com/research/april-23-postmortem) | [03-2026-04-23-claude-code-quality-reports.md](articles/03-2026-04-23-claude-code-quality-reports.md) |
| 2026-04-08 | Scaling Managed Agents: Decoupling the brain from the hands | 规模化 Managed Agents：把大脑与双手解耦 | 全文翻译 | [原文](https://www.anthropic.com/research/managed-agents) | [04-2026-04-08-scaling-managed-agents.md](articles/04-2026-04-08-scaling-managed-agents.md) |
| 2026-03-25 | How we built Claude Code auto mode: a safer way to skip permissions | 我们如何构建 Claude Code 的 auto mode：一种更安全地跳过权限的方式 | 全文翻译 | [原文](https://www.anthropic.com/research/claude-code-auto-mode) | [05-2026-03-25-claude-code-auto-mode.md](articles/05-2026-03-25-claude-code-auto-mode.md) |
| 2026-03-24 | Harness design for long-running application development | 面向长时运行应用开发的 Harness 设计 | 全文翻译 | [原文](https://www.anthropic.com/research/harness-design-long-running-apps) | [06-2026-03-24-harness-design-for-long-running-apps.md](articles/06-2026-03-24-harness-design-for-long-running-apps.md) |
| 2026-03-23 | Long-running Claude for scientific computing | 面向科学计算的长时运行 Claude | 中文摘要 | [原文](https://www.anthropic.com/research/long-running-claude) | [07-2026-03-23-long-running-claude-for-scientific-computing.md](articles/07-2026-03-23-long-running-claude-for-scientific-computing.md) |
| 2026-03-06 | Eval awareness in Claude Opus 4.6’s BrowseComp performance | Claude Opus 4.6 在 BrowseComp 表现中的评估觉察 | 中文摘要 | [原文](https://www.anthropic.com/research/eval-awareness-browsecomp) | [08-2026-03-06-eval-awareness-browsecomp.md](articles/08-2026-03-06-eval-awareness-browsecomp.md) |
| 2026-02-05 | Building a C compiler with a team of parallel Claudes | 用一组并行的 Claude 构建 C 编译器 | 中文摘要 | [原文](https://www.anthropic.com/research/building-c-compiler) | [09-2026-02-05-building-a-c-compiler-with-parallel-claudes.md](articles/09-2026-02-05-building-a-c-compiler-with-parallel-claudes.md) |
| 2026-02-05 | Quantifying infrastructure noise in agentic coding evals | 量化智能体式编程评估中的基础设施噪声 | 中文摘要 | [原文](https://www.anthropic.com/research/infrastructure-noise) | [10-2026-02-05-quantifying-infrastructure-noise.md](articles/10-2026-02-05-quantifying-infrastructure-noise.md) |
| 2026-01-21 | Designing AI-resistant technical evaluations | 设计抗 AI 的技术评估 | 中文摘要 | [原文](https://www.anthropic.com/research/AI-resistant-technical-evaluations) | [11-2026-01-21-designing-ai-resistant-technical-evaluations.md](articles/11-2026-01-21-designing-ai-resistant-technical-evaluations.md) |
| 2026-01-09 | Demystifying evals for AI agents | 揭开 AI 智能体评估的神秘面纱 | 全文翻译 | [原文](https://www.anthropic.com/research/demystifying-evals-for-ai-agents) | [12-2026-01-09-demystifying-evals-for-ai-agents.md](articles/12-2026-01-09-demystifying-evals-for-ai-agents.md) |
| 2025-11-26 | Effective harnesses for long-running agents | 为长时运行智能体设计有效的 Harness | 全文翻译 | [原文](https://www.anthropic.com/research/effective-harnesses-for-long-running-agents) | [13-2025-11-26-effective-harnesses-for-long-running-agents.md](articles/13-2025-11-26-effective-harnesses-for-long-running-agents.md) |
| 2025-11-24 | Introducing advanced tool use on the Claude Developer Platform | 在 Claude Developer Platform 上推出高级工具使用 | 全文翻译 | [原文](https://www.anthropic.com/research/advanced-tool-use) | [14-2025-11-24-introducing-advanced-tool-use.md](articles/14-2025-11-24-introducing-advanced-tool-use.md) |
| 2025-11-04 | Code execution with MCP: Building more efficient agents | 结合 MCP 的代码执行：构建更高效的智能体 | 全文翻译 | [原文](https://www.anthropic.com/research/code-execution-with-mcp) | [15-2025-11-04-code-execution-with-mcp.md](articles/15-2025-11-04-code-execution-with-mcp.md) |
| 2025-10-20 | Beyond permission prompts: making Claude Code more secure and autonomous | 超越权限提示：让 Claude Code 更安全、更自主 | 全文翻译 | [原文](https://www.anthropic.com/research/claude-code-sandboxing) | [16-2025-10-20-beyond-permission-prompts-claude-code-sandboxing.md](articles/16-2025-10-20-beyond-permission-prompts-claude-code-sandboxing.md) |
| 2025-10-16<br>更新：2025-12-18 | Equipping agents for the real world with Agent Skills | 用 Agent Skills 为智能体配备真实世界能力 | 全文翻译 | [原文](https://www.anthropic.com/research/equipping-agents-for-the-real-world-with-agent-skills) | [17-2025-10-16-equipping-agents-for-the-real-world-with-agent-skills.md](articles/17-2025-10-16-equipping-agents-for-the-real-world-with-agent-skills.md) |
| 2025-09-29 | Building agents with the Claude Agent SDK | 用 Claude Agent SDK 构建智能体 | 全文翻译 | [原文](https://claude.com/resources/articles/building-agents-with-the-claude-agent-sdk) | [18-2025-09-29-building-agents-with-the-claude-agent-sdk.md](articles/18-2025-09-29-building-agents-with-the-claude-agent-sdk.md) |
| 2025-09-29 | Effective context engineering for AI agents | 面向 AI 智能体的有效 Context Engineering | 全文翻译 | [原文](https://www.anthropic.com/research/effective-context-engineering-for-ai-agents) | [19-2025-09-29-effective-context-engineering-for-ai-agents.md](articles/19-2025-09-29-effective-context-engineering-for-ai-agents.md) |
| 2025-09-29 | Enabling Claude Code to work more autonomously | 让 Claude Code 更能自主工作 | 中文摘要 | [原文](https://www.anthropic.com/news/enabling-claude-code-to-work-more-autonomously) | [20-2025-09-29-enabling-claude-code-to-work-more-autonomously.md](articles/20-2025-09-29-enabling-claude-code-to-work-more-autonomously.md) |
| 2025-09-11 | Writing effective tools for agents — with agents | 为智能体撰写有效工具——与智能体一起 | 全文翻译 | [原文](https://www.anthropic.com/research/writing-tools-for-agents) | [21-2025-09-11-writing-effective-tools-for-agents.md](articles/21-2025-09-11-writing-effective-tools-for-agents.md) |
| 2025-06-26<br>更新：2025-09-11 | Desktop Extensions: One-click MCP server installation for Claude Desktop | Desktop Extensions：为 Claude Desktop 一键安装 MCP server | 中文摘要 | [原文](https://www.anthropic.com/research/desktop-extensions) | [22-2025-06-26-desktop-extensions.md](articles/22-2025-06-26-desktop-extensions.md) |
| 2025-06-13 | How we built our multi-agent research system | 我们如何构建多智能体研究系统 | 全文翻译 | [原文](https://www.anthropic.com/research/multi-agent-research-system) | [23-2025-06-13-how-we-built-our-multi-agent-research-system.md](articles/23-2025-06-13-how-we-built-our-multi-agent-research-system.md) |
| 2025-04-18<br>更新：2026-01-26 | Claude Code: Best practices for agentic coding | Claude Code：智能体式编程最佳实践 | 全文翻译 | [原文](https://www.anthropic.com/research/claude-code-best-practices) | [24-2025-04-18-claude-code-best-practices.md](articles/24-2025-04-18-claude-code-best-practices.md) |
| 2025-03-20<br>更新：2025-12-15 | The "think" tool: Enabling Claude to stop and think in complex tool use situations | “Think” 工具：让 Claude 在复杂工具使用场景中停下来思考 | 全文翻译 | [原文](https://www.anthropic.com/research/claude-think-tool) | [25-2025-03-20-the-think-tool.md](articles/25-2025-03-20-the-think-tool.md) |
| 2024-12-19 | Building effective agents | 构建有效的智能体 | 全文翻译 | [原文](https://www.anthropic.com/research/building-effective-agents) | [26-2024-12-19-building-effective-agents.md](articles/26-2024-12-19-building-effective-agents.md) |

同一天发表的文章保持原先的英文标题字母序，不随整体倒序打乱。

## 翻译与整理说明

- 全文翻译力求忠实、完整；代码块保持原样，MCP、SDK、harness、context window、prompt injection、compaction、sandbox 等技术术语保留英文。
- 原文中的配图未逐一复制，而以简要文字说明代替。请以官方原文中的图表为准。
- 各篇 Markdown 页眉均标明：英文标题、中文标题、发布日期（如有则另列更新日期）、原文链接、翻译类型（全文翻译 / 中文摘要）。
- 部分文章日后有官方更新或维护说明（例如 think 工具建议改用 extended thinking、Claude Code best practices 已迁至文档、Desktop Extensions 扩展名改为 `.mcpb`），已在对应页眉的「更新日期」或正文中注明。
- 工程博文多数发布在 `anthropic.com/research/...`。「Building agents with the Claude Agent SDK」发布在 [claude.com](https://claude.com/resources/articles/building-agents-with-the-claude-agent-sdk)；「Enabling Claude Code to work more autonomously」发布在新闻频道。

## 版权与使用说明

原文版权归 [Anthropic](https://www.anthropic.com/) 所有。本仓库中的中文翻译与摘要仅供个人学习与研究使用，不构成对原文的官方译本，也不主张对原文内容享有权利。请通过各篇页眉与上表中的「原文」链接阅读官方出处；转载或引用时请同时注明原作者与原文链接，并遵守 Anthropic 的使用条款。

如需引用或核对，一律以 Anthropic 官方页面为准。
