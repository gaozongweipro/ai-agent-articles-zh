---
title_en: How we contain Claude across products
title_zh: 我们如何在各产品中约束 Claude
company: anthropic
date: 2026-05-25
url: https://www.anthropic.com/research/how-we-contain-claude
type: summary
category: 安全与沙箱
tags:
  - 安全
  - 沙箱
  - Claude
  - 防护
---

# 我们如何在各产品中约束 Claude

随着智能体能力与访问权限扩大，失败概率因安全和训练进展下降，但理论爆炸半径在增大。不部署的成本也在变大。工程问题变成如何限制爆炸半径。监督（human-in-the-loop）在理论上可行，但 Claude Code 遥测显示用户批准了约 93% 的权限提示，审批疲劳会削弱监督；auto mode 可以减轻这一点，但任何概率性防御都有非零漏报。因此本文聚焦 **containment（约束/隔离）**：通过 sandbox、虚拟机和出口控制，限制智能体*能够*做什么。

风险分为三类：用户滥用、模型不当行为、外部攻击者（含 prompt injection）。防御对应三层：智能体运行的环境、智能体咨询的模型，以及智能体可触及的外部内容。文章总结三种产品模式及各自错过的风险：

1. **临时容器**（claude.ai 代码执行）：服务端容器，用 gVisor 等隔离。
2. **人在回路中的 sandbox**（Claude Code）：低延迟本地 sandbox；曾错过信任对话框之前的风险，以及用户本身作为注入向量。
3. **本地 VM**（Claude Cowork）：经 vsock 与 hypervisor 边界守卫的挂载工作区；曾错过经已批准域名的外泄，以及 VM 隔离把端点检测软件也挡在外面。

文中强调：远程工具相对本地工具更难审计，因为行为可以在批准后改变；即使工具受信任，工具输出仍是攻击面。展望包括持久记忆投毒、多智能体信任升级，以及智能体身份（凭证留在主机钥匙串，VM 获得按 session 缩小范围的 token）。建议先在环境层设计约束，再在模型层引导行为；使隔离强度与用户监督能力匹配；谨慎对待定制组件，优先使用久经考验的 hypervisor、syscall 过滤器和容器运行时。
