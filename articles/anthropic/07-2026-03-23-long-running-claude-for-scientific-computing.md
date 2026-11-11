---
title_en: Long-running Claude for scientific computing
title_zh: 面向科学计算的长时运行 Claude
company: anthropic
date: 2026-03-23
url: https://www.anthropic.com/research/long-running-claude
type: summary
category: 编码 Agent
tags:
  - 长时任务
  - Claude
  - 科研 Agent
  - 编码 Agent
---

# 面向科学计算的长时运行 Claude

Discovery 团队研究员 Siddharth Mishra-Sharma 说明如何把多日智能体式编程工作流——测试预言机（test oracles）、持久记忆和编排模式——应用到科学计算任务，即使任务不在自己的核心领域内。

许多科学家仍以紧约束的对话循环使用 AI。随着模型在长周期任务上变强，可以指定高层目标，让一组智能体自主工作，在数小时内完成原本可能需要数天、数周甚至数月的项目。适合的任务通常范围清晰、成功标准明确，例如重实现数值求解器、把旧 Fortran 科学软件迁到现代语言、对照参考实现调试大型代码库。

文章以用 Claude Opus 4.6 实现可微分宇宙学 Boltzmann 求解器（[clax](https://github.com/smsharma/clax)）为例：该数值代码预测宇宙微波背景（CMB）的统计性质。可微分版本可以让梯度穿过完整求解器，从而加速基于梯度的推断；用 JAX 实现可免费获得自动微分和加速器兼容性。作者本人对该领域只有高层熟悉。方法受到 Anthropic C 编译器项目（约 2,000 个 sessions）启发，并面向典型学术实验室给出了用 Claude Code 搭建类似模式的实践建议。
