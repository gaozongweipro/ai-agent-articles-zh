# 设计抗 AI 的技术评估

- 英文标题：Designing AI-resistant technical evaluations
- 中文标题：设计抗 AI 的技术评估
- 发布日期：2026-01-21
- 原文链接：https://www.anthropic.com/research/AI-resistant-technical-evaluations
- 翻译类型：中文摘要

---

Anthropic 性能优化团队的 Tristan Hume 讲述他们自 2024 年初以来使用的 take-home 测试：候选人优化面向模拟加速器的代码。已有超过 1,000 名候选人完成该测试，并帮助招聘了数十名性能工程师。设计目标包括较长的时间跨度、真实环境、允许理解系统与构建调试工具、与 AI 辅助兼容、代表真实工作、高信号、不要求狭窄领域知识，以及有趣。

但每个新 Claude 模型都迫使他们重新设计测试。在相同时间限制下，Claude Opus 4 超过了大多数人类申请者；随后 Claude Opus 4.5 追平了最强人类候选人。人类在不限时条件下仍可胜过模型，但在 take-home 的约束下，测试失去了区分力。作者先把起点移到 Opus 4 开始吃力的地方，去掉已被解决的多核部分，并把时限从 4 小时减到 2 小时；Opus 4.5 再次击败了新版本。文章讨论了备选方案，并开放挑战：如何设计在模型持续变强时仍能衡量人类工程能力的技术评估。
