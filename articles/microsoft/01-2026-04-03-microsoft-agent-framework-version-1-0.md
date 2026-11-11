---
title_en: Microsoft Agent Framework Version 1.0
title_zh: Microsoft Agent Framework 1.0 版
company: microsoft
date: 2026-04-03
url: https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-version-1-0/
type: full
category: 框架与 SDK
tags:
  - 框架与 SDK
  - 多 Agent
  - MCP
  - A2A
  - 记忆
  - harness
---

# Microsoft Agent Framework 1.0 版

今天我们兴奋地宣布，Microsoft Agent Framework 的 .NET 与 Python 版本都已到达 1.0。这是面向生产的发布：稳定的 API，以及对长期支持的承诺。无论你是在构建单个助手，还是编排一组专业化智能体，Agent Framework 1.0 都提供企业级的多智能体编排、多提供商模型支持，以及通过 A2A 与 MCP 实现的跨运行时互操作。

当我们在去年 10 月介绍 Microsoft Agent Framework 时，目标是把 Semantic Kernel 面向企业的基础与 AutoGen 的创新编排统一到同一个开源 SDK 中。今年 2 月进入 Release Candidate 后，我们锁定了功能面，并邀请社区充分试用。今天，在数月的反馈、加固以及与客户和合作伙伴的实际验证之后，Agent Framework 1.0 已为生产做好准备。

## 创建你的第一个智能体

开始只需几行代码。下面是在两种语言中创建简单智能体的方式。

Python：

```python
# pip install agent-framework
# Use `az login` to authenticate with Azure CLI

import asyncio

from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential

agent = Agent(
    client= FoundryChatClient(
      project_endpoint="https://your-project.services.ai.azure.com",
      model="gpt-5.3",
      credential=AzureCliCredential(),
    ),
    name="HelloAgent",
    instructions="You are a friendly assistant."
)

print(asyncio.run(agent.run("Write a haiku about shipping 1.0.")))
```

.NET：

```csharp
// dotnet add package Microsoft.Agents.AI.OpenAI --prerelease
using Microsoft.Agents.AI;
using Microsoft.Agents.AI.Foundry;
using Azure.Identity;

var agent = new AIProjectClient(endpoint:"https://your-project.services.ai.azure.com")
    .GetResponsesClient("gpt-5.3")
    .AsAIAgent(
        name: "HaikuBot",
        instructions: "You are an upbeat assistant that writes beautifully."
    );

Console.WriteLine(await agent.RunAsync("Write a haiku about shipping 1.0."));
```

就是这样——只需少量代码就得到一个可用的 AI 智能体。从此可以添加函数工具、多轮会话、流式响应等。

## 多智能体工作流

单个智能体已经很有用，但现实应用常常需要多个智能体协同。下面是一个顺序工作流：文案撰写智能体起草标语，评审智能体给出反馈。

```python
import asyncio

from agent_framework import Agent, Message
from agent_framework.foundry import FoundryChatClient
from agent_framework.orchestrations import SequentialBuilder
from azure.identity import AzureCliCredential

async def main() -> None:
    client = FoundryChatClient(credential=AzureCliCredential())

    writer = Agent(
        client=client,
        instructions="You are a concise copywriter. Provide a single, punchy marketing sentence.",
        name="writer",
    )

    reviewer = Agent(
        client=client,
        instructions="You are a thoughtful reviewer. Give brief feedback on the previous message.",
        name="reviewer",
    )

    workflow = SequentialBuilder(participants=[writer, reviewer]).build()
    outputs: list[list[Message]] = []
    async for event in workflow.run("Write a tagline for Microsoft Agent Framework 1.0.", stream=True):
        if event.type == "output":
            outputs.append(event.data)
    if outputs:
        for msg in outputs[-1]:
            print(f"[{msg.author_name or 'user'}]: {msg.text}")

if __name__ == "__main__":
    asyncio.run(main())
```

.NET 版本见原文的 Getting Started with Workflows。

## 1.0 包含什么

1.0 代表我们已经过实战检验、稳定下来、并承诺向后兼容的功能。

- 单智能体与服务连接器：核心智能体抽象在 .NET 与 Python 上均已稳定、可用于生产。框架提供面向 Microsoft Foundry、Azure OpenAI、OpenAI、Anthropic Claude、Amazon Bedrock、Google Gemini 与 Ollama 的第一方连接器。
- 中间件钩子：可在执行的每个阶段拦截、变换和扩展智能体行为——内容安全过滤、日志、合规策略、自定义逻辑——而无需修改智能体提示。
- 智能体记忆与上下文提供器：可插拔的记忆架构，支持会话历史、持久键值状态和基于向量的检索。可选择 Foundry Agent Service 中的 Memory、Mem0、Redis、Neo4j 或自定义存储。
- 智能体工作流：用于把智能体和函数组成确定性、可重复流程的图工作流引擎现已稳定。可把智能体推理与业务逻辑结合，按条件分支、并行展开并汇合结果。检查点与 hydration 确保长时流程能在中断后恢复。
- 多智能体编排：稳定支持源自 Microsoft Research 与 AutoGen 的模式：顺序、并发、handoff、群聊和 Magentic-One。所有模式都支持流式、检查点、人在环中审批，以及长时工作流的暂停/恢复。
- 声明式智能体与工作流（YAML）：在可版本控制的 YAML 中定义指令、工具、记忆配置和编排拓扑，然后用一次 API 调用加载并运行。
- A2A 与 MCP：MCP 支持让智能体动态发现并调用 MCP 兼容服务器上的外部工具。A2A 支持跨运行时协作（A2A 1.0 支持即将到来）——你的智能体可以用结构化、协议驱动的消息，与运行在其他框架中的智能体协调。
- 迁移助手（Semantic Kernel 与 AutoGen）：为来自这两套体系的团队分析现有代码并生成逐步迁移计划。详见官方迁移指南。

## 自 10 月发布以来的新内容

我们同时也带上若干预览功能，可供早期采用；这些 API 在变为「稳定」前可能随社区反馈演化。

- DevUI：基于浏览器的本地调试器，用于实时可视化智能体执行、消息流、工具调用和编排决策。
- Foundry 托管智能体集成：把 Agent Framework 智能体作为 Microsoft Foundry 上的托管服务或 Azure Durable Functions 运行。
- Foundry 工具、记忆、可观测性与评估：与 Foundry 的托管工具生态、记忆以及基于 OpenTelemetry 的可观测性和评估仪表盘深度集成。
- AG-UI / CopilotKit / ChatKit：把智能体输出流式传到前端，包括工具执行状态和人在环中流程。
- Skills：可复用的领域能力包（指令 + 脚本 + 资源），让智能体开箱获得结构化能力。
- GitHub Copilot SDK 与 Claude Code SDK：可从 Agent Framework 编排代码中直接把这些 SDK 当作智能体 harness 使用。它们处理自主循环——规划、工具执行、文件编辑和会话管理——而 Agent Framework 负责把它们与其他智能体组合在同一多智能体工作流中。
- Agent Harness：可定制的框架 harness 与本地运行时，让智能体访问 shell、文件系统和消息循环，适用于编码智能体、自动化和个人助手模式。

## 开始使用

若你一直在使用 RC 包，升级到 1.0 只需提升包版本。若你是新用户：

```text
pip install agent-framework
```

```text
dotnet add package Microsoft.Agents.AI
```

请参阅快速入门指南或 GitHub 上的示例。来自 AutoGen 或 Semantic Kernel？现在是迁移到 Microsoft Agent Framework 的时机。

## 下一步

1.0 是开始而非终点。我们将继续把预览功能升级为稳定版，扩展连接器与 skills 生态，加深 Foundry 集成，并纳入 Microsoft Research 的最新编排研究。框架 100% 开源。感谢所有提交 issue、PR、测试 RC 并推动框架改进的人。

入口：aka.ms/AgentFramework、文档 aka.ms/AgentFramework/Docs、GitHub `microsoft/agent-framework`，以及 NuGet 包 `Microsoft.Agents.AI` 与 PyPI 包 `agent-framework`。
