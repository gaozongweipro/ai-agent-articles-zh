---
title_en: "DeepSeek-V3.2: Pushing the Frontier of Open Large Language Models (Tech Report)"
title_zh: DeepSeek-V3.2 技术报告（摘要）：推动开源大语言模型的前沿
company: deepseek
date: 2025-12-01
url: https://arxiv.org/abs/2512.02556
type: summary
category: 模型与发布
tags:
  - 工具调用
  - thinking
  - Agent 训练
  - 评测
  - 模型发布
---

# DeepSeek-V3.2 技术报告（摘要）：推动开源大语言模型的前沿

官方技术报告（arXiv:2512.02556，与 2025-12-01 的 V3.2 发布说明同日）介绍 DeepSeek-V3.2 如何在计算效率、推理与智能体性能之间取得平衡。与 Agent 开发最直接相关的，是把思考过程整合进工具使用：模型可在 thinking / non-thinking 两种模式下调用工具；在带 `tools` 的多轮请求中，需要把先前轮次的 `reasoning_content` 完整回传，才能保持推理链条。报告还描述了大规模智能体任务合成流水线，用于在工具场景中训练「边思考、边调用工具」的能力。V3.2-Speciale 侧重极限推理评测，官方说明其不支持工具调用。完整方法、基准与训练细节请阅读 arXiv 论文及 Hugging Face 上的技术报告。
