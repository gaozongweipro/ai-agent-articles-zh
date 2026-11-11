---
title_en: "The Building Blocks of Agentic AI: From Kernels to Clusters"
title_zh: 智能体 AI 的构建模块：从内核到集群
company: meta
date: 2025-10-24
url: https://ai.meta.com/blog/introducing-pytorch-native-agentic-stack/
type: summary
category: 框架与 SDK
tags:
  - 框架与 SDK
  - Agent 训练
  - 评测
  - 编码 Agent
  - PyTorch
---

# 智能体 AI 的构建模块：从内核到集群

Meta 在 2025 年 PyTorch Conference 上公布一套面向智能体 AI 生命周期的 PyTorch 原生工具（官方日期为 2025-10-24）。文章重点不是应用层「如何写一个客服 Agent」，而是训练、部署与扩展智能体系统的基础设施：Helion 用于更简洁地编写加速器 kernel；Torchcomms 提供大规模容错通信；Monarch 以单控制器简化集群执行；Torchforge 把强化学习后训练与智能体开发中的基础设施和算法关注点分开，便于在数千 GPU 上做同步/异步 RL；ExecuTorch 1.0 支持在手机与边缘设备部署模型；并与 Hugging Face 合作推出 OpenEnv，作为开放的 RL 环境中心与接口规范（RFC）。原则是可扩展、PyTorch 原生、面向异构硬件。对想了解智能体训练环境与后训练栈的读者有参考价值；应用层编排与工具调用细节需另见各产品文档。项目入口见 meta-pytorch.org。
