---
title_en: Introducing Operator
title_zh: 介绍 Operator
company: openai
date: 2025-01-23
updated: 2025-07-17
url: https://openai.com/index/introducing-operator/
type: summary
category: 工具与协议
tags:
  - Computer Use
  - 安全
  - 编码 Agent
  - 工具调用
  - Operator
---

# 介绍 Operator

OpenAI 于 2025 年 1 月 23 日发布 Operator 研究预览：一个可使用自有浏览器、通过点击、输入和滚动代用户完成网页任务的智能体，由 Computer-Using Agent（CUA）模型驱动。CUA 结合 GPT-4o 的视觉能力与强化学习推理，直接操作 GUI，而无需网站专用 API；遇阻时可自我纠正或交还控制权。页面 2025-07-17 更新指出：Operator 已完全并入 ChatGPT，以 composer 中的 “agent mode” 提供，独立站点将在随后数周下线。

安全设计强调用户始终可控：敏感信息进入 takeover mode（此时不采集用户输入）；提交订单或发送邮件前需确认；对银行等更高风险任务会拒绝或要求密切监督（watch mode）。另有针对提示注入的谨慎导航、监控模型与检测流水线。当时仍属早期预览，复杂界面上可能出错。更详细的方法与评测见同日的 [Computer-Using Agent](https://openai.com/index/computer-using-agent/) 研究博文。
