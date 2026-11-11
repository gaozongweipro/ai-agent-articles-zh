---
title_en: Agent2Agent protocol (A2A) is getting an upgrade
title_zh: Agent2Agent 协议（A2A）迎来升级
company: google
date: 2025-07-31
url: https://cloud.google.com/blog/products/ai-machine-learning/agent2agent-protocol-is-getting-an-upgrade
type: full
category: 工具与协议
tags:
  - A2A
  - ADK
  - 多 Agent
  - 评测
  - 协议
---

# Agent2Agent 协议（A2A）迎来升级

宣布在 Google Cloud 上扩展 A2A 智能体的完整开发者工具包。

编辑注：Agentspace 现已成为 Gemini Enterprise 的一部分。支撑 Agentspace 的智能体创建与编排技术，现在正为 Gemini Enterprise 平台的核心功能提供动力。

AI 正在从单一、针对特定任务的智能体，演进为一个互联生态，其中自主智能体无论底层平台如何，都能协作解决复杂问题。为使开发者更容易完成这一转变，我们宣布一套全面的工具，赋能开发者在 Google Cloud 上构建、部署、评估并销售 Agent2Agent（A2A）智能体。

今天，我们兴奋地宣布发布 A2A 协议 0.3 版本，它带来更稳定的构建接口，对加速企业采用至关重要。该版本引入若干关键能力，包括 gRPC 支持、签署安全卡片（security cards）的能力，以及 Python SDK 中扩展的客户端支持，从而提供更灵活的使用、更好的安全性和更容易的集成。

A2A 协议正迅速获得动量，得到一个不断增长的、超过 150 个组织的生态支持，涵盖每一个主要的超大规模云、领先技术提供商，以及使用 Google Cloud 的跨国客户。企业已经在为其组织构建强大能力。例如，Tyson Foods 和 Gordon Food Service 正在开创协作式 A2A 系统，以推动销售并减少供应链摩擦，为它们的智能体创建一个实时通道，共享产品数据和线索，从而增强食品供应链。

### 构建：在 Agent Development Kit（ADK）中原生支持 A2A

我们正在为 Google 发布的强大开源智能体框架 Agent Development Kit（ADK）发布对 A2A 的原生支持。如果你已经在使用 ADK，这将使构建 A2A 智能体变得容易，并且建立在我们先前发布的 A2A SDK 之上。例如，用一个简单的 “Hello, World!” 风格代码片段，开发者现在可以用 ADK：

- 使用带有 Agent Card 的 A2A 智能体，并把它当作子智能体使用。
- 把现有的 ADK 智能体暴露出来，使其可作为 A2A 智能体被发现。

开发者今天就可以开始用 ADK 构建协作智能体。

### 部署：使用 Agent Engine、Cloud Run 和 GKE 的灵活部署选项

智能体构建完成后，它们需要一个稳健、可扩展的家园。我们提供三条强大的部署路径，供客户把智能体扩展到生产：

- 部署到 Agent Engine：对于托管的、为智能体优化的环境，Agent Engine 是许多智能体构建者的选择。我们将在随后数周为 Agent Engine 增加对 A2A 的支持，使你能轻松地把用任何框架编写的智能体部署到 Agent Engine，并得到一个可投产的、Google 规模的 A2A 智能体。
- 部署到 Cloud Run：为获得更大灵活性，你可以把 A2A 智能体容器化并部署到 Cloud Run，利用 Google 的无服务器基础设施获得大规模和可靠性。请遵循已发布的指南。
- 部署到 Google Kubernetes Engine（GKE）：为获得最大控制，你可以把智能体部署到 GKE，利用 Kubernetes 的全部能力来大规模管理 A2A 系统。

随着随后数周对 A2A 支持的到来，开发者将能使用 `agent-starter-pack` CLI 工具，仅用一行完成 CI/CD 设置：

```
uvx agent-starter-pack create my-agent -a adk@gemini-fullstack
```

### 集成：通过 Agentspace 把 A2A 智能体带给用户

智能体需要安全、可及的环境才能有用。这就是我们构建 Agentspace 的原因，它是智能体与终端用户相遇的目的地。在随后数周，合作伙伴将能在 Agentspace 中提供任何 A2A 智能体，把它从独立工具转变为人们可以消费的有价值服务。这包括构建在合作伙伴平台上的合作伙伴智能体，使客户能在多个位置访问这些 A2A 智能体。

Agentspace 不只是一个中心，还提供企业级智能体平台所需的关键治理、安全和控制功能，确保交互安全可靠。

### 评估并商业化你的 A2A 系统

构建和部署智能体只是开始。要创建真正企业级的系统，你需要稳健的评估能力，这就是为什么我们正在把 Vertex GenAI Evaluation Service 扩展到支持 A2A 智能体评估。请参阅我们的实践指导。

### 在 AI Agent Marketplace 中发现并销售合作伙伴构建的 A2A 智能体

合作伙伴现在可以直接在 AI Agent Marketplace 中向客户销售其 A2A 智能体。这将允许 Google Cloud 客户发现并购买由 ISV、GSI 和其他技术提供商发布的智能体。AI Agent Marketplace 为希望将其 AI 智能体货币化的合作伙伴提供了重要的市场路径。

合作伙伴可以在此请求更多信息。

### A2A 生态正在增长

我们在 4 月宣布 A2A 协议，以引领行业走向可互操作的智能体系统；并在 6 月通过把它贡献给 Linux Foundation 推进了这一承诺。行业的响应持续增长，反映出对供应商中立、社区驱动标准的共同信念。Google Cloud 的许多合作伙伴此前已向共同客户提供智能体，他们现在正为这些智能体启用 A2A，以帮助为客户的投资面向未来。

- Adobe：作为生成式 AI 的领导者，Adobe 正在利用 A2A 协议，使其快速增长的分布式智能体能够与 Google Cloud 生态中的智能体互操作。A2A 协议使 Adobe 智能体能够在企业中协作，创造强大的新数字体验，简化优化内容创作过程的工作流，并自动化多系统流程与数据集成。
- S&P Global Market Intelligence：S&P 已采用 A2A 作为智能体间通信协议。这一战略对齐增强了该组织智能体生态的互操作性、可扩展性和面向未来的能力。
- ServiceNow：作为 A2A 的创始合作伙伴，ServiceNow 通过其 AI Agent Fabric——连接 ServiceNow、客户和合作伙伴构建之智能体的多智能体通信层——赋能客户。这为企业提供释放智能体 AI 全部潜力所需的更大选择与灵活性，带来更快决策、更少交接和更可扩展的方案。
- Twilio：Twilio 正在使用 A2A 协议实现延迟感知的智能体选择。通过扩展 A2A 协议，各个智能体现在广播其延迟，使系统能智能地把任务路由到当前最响应的可用智能体，并优雅地适应——例如，如果高延迟智能体是唯一选项，则播放填充提示或添加打字音。

开发者可以在发布说明中了解过去的版本，在路线图中了解即将到来的内容，并加入社区帮助演进协议。社区还围绕 A2A 发布了出色的工具，包括 A2A Inspector 和 Technology Compatibility Kit。

### 开始使用

我们兴奋地与整个行业合作构建人工智能的未来。原文提供了开始构建、部署和参与社区的入口。我们迫不及待想看到你的构建。
