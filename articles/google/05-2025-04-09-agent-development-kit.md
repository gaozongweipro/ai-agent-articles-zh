---
title_en: "Agent Development Kit: Making it easy to build multi-agent applications"
title_zh: Agent Development Kit：让构建多智能体应用变得容易
company: google
date: 2025-04-09
url: https://developers.googleblog.com/en/agent-development-kit-easy-to-build-multi-agent-applications/
type: full
category: 框架与 SDK
tags:
  - ADK
  - 多 Agent
  - MCP
  - 评测
  - 框架与 SDK
---

# Agent Development Kit：让构建多智能体应用变得容易

AI 世界正在迅速超越单一用途模型，走向智能、自主的多智能体系统。然而，构建这些多智能体系统带来了新的挑战。正因为如此，我们今天在 Google Cloud NEXT 2025 上推出了 Agent Development Kit（ADK），这是来自 Google 的新开源框架，旨在简化智能体和多智能体系统的全栈、端到端开发。ADK 赋能开发者像你一样，以更大的灵活性和精确控制构建可投产的智能体应用。

ADK 是为 Agentspace 和 Google Customer Engagement Suite（CES）等 Google 产品中的智能体提供动力的同一框架。通过开源 ADK，我们旨在为开发者提供强大、灵活的工具，以便在快速演进的智能体图景中进行构建。ADK 被设计为灵活的，可以使用不同模型，并为不同部署环境构建可投产的智能体。

## ADK 的核心支柱：构建、交互、评估、部署

ADK 在整个智能体开发生命周期中提供能力：

- 天生的多智能体：通过在层级中组合多个专业智能体，构建模块化、可扩展的应用。实现复杂的协调与委托。
- 丰富的模型生态：选择最适合你需求的模型。ADK 可与你选择的模型一起工作——无论是 Gemini，还是可通过 Vertex AI Model Garden 访问的任何模型。该框架还提供 LiteLLM 集成，让你可以从 Anthropic、Meta、Mistral AI、AI21 Labs 等众多提供商的模型中选择。
- 丰富的工具生态：为智能体配备多样能力：使用预构建工具（Search、Code Exec）、Model Context Protocol（MCP）工具，集成第三方库（LangChain、LlamaIndex），甚至把其他智能体当作工具（LangGraph、CrewAI 等）。
- 内置流式：通过 ADK 独特的双向音频和视频流能力，以类似人类的对话与智能体交互。只需几行代码，你就可以创建改变你与智能体协作方式的自然交互——从文本走向丰富的多模态对话。
- 灵活编排：使用工作流智能体（`Sequential`、`Parallel`、`Loop`）定义可预测的流水线，或利用 LLM 驱动的动态路由（`LlmAgent` transfer）实现自适应行为。
- 集成的开发者体验：用强大的 CLI 和可视化 Web UI 在本地开发、测试和调试。逐步检查事件、状态和智能体执行。
- 内置评估：通过对照预定义测试用例，同时评估最终回复质量和逐步执行轨迹，系统地评估智能体表现。
- 轻松部署：把智能体容器化并部署到任何地方。

## 开始构建你的第一个智能体

虽然我们鼓励你探索文档中的示例，但核心思想是 Pythonic 的简洁。你定义智能体的逻辑、它可以使用的工具，以及它应如何处理信息。ADK 提供管理状态、编排工具调用以及与底层 LLM 交互的结构。下面是一个基本智能体的示意例子。

代码可见快速入门指南。

```python
from google.adk.agents import LlmAgent
from google.adk.tools import google_search

dice_agent = LlmAgent(
    model="gemini-2.0-flash-exp",  # Required: Specify the LLM
    name="question_answer_agent",  # Required: Unique agent name
    description="A helpful assistant agent that can answer questions.",
    instruction="""Respond to the query using google search""",
    tools=[google_search],  # Provide an instance of the tool
)

# you can run this by using adk web
```

这个简单例子展示了基本结构。当构建涉及多个智能体、复杂工具使用和动态编排、同时保持控制的更复杂应用时，ADK 真正闪耀。

ADK 在你与智能体交互的方式上提供灵活性：CLI、Web UI、API Server 和 API（Python）。你定义智能体（`agent.py` 中的核心逻辑）的方式，无论选择哪种交互方式都相同。差异在于你如何发起和管理交互。所有这些都可在 ADK 文档中找到示例。

## 用 ADK 构建多智能体应用

当你从单个智能体走向构建利用工具的协作多智能体系统时，ADK 真正闪耀。想象创建一个专业智能体团队，其中主智能体可以根据对话委托任务。ADK 通过层级结构和智能路由使这一切变得容易。

让我们走一个示意例子——一个处理天气查询、但把问候委托给专门 GreetingAgent 的 `WeatherAgent`。

1. 定义工具：智能体使用工具来执行动作。这里，我们的 `WeatherAgent` 需要一个获取天气数据的工具。我们定义一个 Python 函数；ADK 使用其 `docstring` 来理解何时以及如何使用它。

```python
def get_weather(city: str) -> dict:
    # Best Practice: Log tool execution for easier debugging
    print(f"--- Tool: get_weather called for city: {city} ---")
    city_normalized = city.lower().replace(" ", "")

    mock_weather_db = {
        "newyork": {"status": "success", "report": "The weather in New York is sunny with a temperature of 25°C."},
        "london": {"status": "success", "report": "It's cloudy in London with a temperature of 15°C."},
        "tokyo": {"status": "success", "report": "Tokyo is experiencing light rain and a temperature of 18°C."},
        "chicago": {"status": "success", "report": "The weather in Chicago is sunny with a temperature of 25°C."},
        "toronto": {"status": "success", "report": "It's partly cloudy in Toronto with a temperature of 30°C."},
        "chennai": {"status": "success", "report": "It's rainy in Chennai with a temperature of 15°C."},
    }

    if city_normalized in mock_weather_db:
        return mock_weather_db[city_normalized]
    else:
        return {"status": "error", "error_message": f"Sorry, I don't have weather information for '{city}'."}
```

2. 定义智能体及其关系：我们使用 `LlmAgent`（或 `Agent`）创建智能体。请特别注意 `instruction` 和 `description` 字段——LLM 在很大程度上依赖它们来理解角色，并使用对子智能体的自动委托来做出委托决策。

```python
greeting_agent = Agent(
    model=LiteLlm(model="anthropic/claude-3-sonnet-20240229"),
    name="greeting_agent",
    instruction="You are the Greeting Agent. Your ONLY task is to provide a friendly greeting to the user. "
                "Do not engage in any other conversation or tasks.",
    description="Handles simple greetings and hellos",
)

farewell_agent = Agent(
    model=LiteLlm(model="anthropic/claude-3-sonnet-20240229"),
    name="farewell_agent",
    instruction="You are the Farewell Agent. Your ONLY task is to provide a polite goodbye message. "
                "Do not perform any other actions.",
    description="Handles simple farewells and goodbyes",
)

root_agent = Agent(
    name="weather_agent_v2",
    model="gemini-2.0-flash-exp",
    description="You are the main Weather Agent, coordinating a team. - Your main task: Provide weather using the `get_weather` tool. Handle its 'status' response ('report' or 'error_message'). - Delegation Rules: - If the user gives a simple greeting (like 'Hi', 'Hello'), delegate to `greeting_agent`. - If the user gives a simple farewell (like 'Bye', 'See you'), delegate to `farewell_agent`. - Handle weather requests yourself using `get_weather`. - For other queries, state clearly if you cannot handle them.",
    tools=[get_weather],
    sub_agents=[greeting_agent, farewell_agent]
)
```

### 委托如何工作

- 默认的智能体行为是允许委托。
- 在处理用户消息时，LLM 会考虑查询、当前智能体的 `description`，以及相关智能体（层级中定义的父/子智能体）的 `description` 字段。
- 如果 LLM 根据描述判定另一个智能体更合适（例如用户说 “Hi”，与 `GreetingAgent` 的描述匹配），它就会发起转移。

清晰、有区分度的描述至关重要！LLM 用它们来有效路由任务。

在这一设置中，如果用户以 “Hi” 开始，作为处理输入的根智能体的 `WeatherAgent` 可以识别这不是天气查询，通过描述看到 `GreetingAgent` 合适，并自动转移控制权。如果用户问 “What's the weather in Chicago?”，`WeatherAgent` 会使用其 `get_weather` 工具直接处理。

这个例子展示了 ADK 的层级结构和由描述驱动的委托，如何让你构建有组织、可维护且复杂的多智能体应用。

## 完成生命周期：评估与部署

构建像我们的天气智能体这样的智能智能体是基础，但可靠地把它们带给用户涉及关键的下一步：严格评估和无缝部署。在上线前，确保你的智能体行为可预期且正确至关重要。ADK 的集成评估工具正是为此而设计，让你对照预定义数据集（如 `evaluation.test.json` 或 `test.json`）系统地测试执行路径和回复质量。你可以在测试套件中用 `AgentEvaluator.evaluate()` 以编程方式运行这些检查，也可以通过 ADK eval 命令行工具或 Web UI 直接使用评估。

一旦你对表现满意，ADK 通过部署到任何容器运行时的选项，或与 Vertex AI Agent Engine 的集成，提供清晰、精简的生产路径。这让你能够利用完全托管、可扩展且企业级的运行时，完成开发生命周期，并赋能你从复杂原型走向稳健、可投产的智能体应用。

## 为你选择框架：ADK 还是 Genkit？

当你探索用 ADK 构建多智能体系统的可能性时，可能想知道它如何融入 Google 更广泛的 GenAI 开发工具图景。虽然有包括 Genkit 框架在内的多种 SDK 和框架可用，了解 ADK 的相对重点会有帮助。下面是一个简要比较：

### Agent Development Kit

- 针对复杂智能体和多智能体系统做了优化，为智能体开发提供更高层的抽象，并内置对 LiteLLM 和 Vertex AI Model Garden 的集成，以支持多种模型。
- 聚焦于定义智能体行为与交互。
- 支持双向流式。

### Genkit

- 为构建大量 AI 驱动体验提供基础构建块。
- 包含用于迭代、测试和调试 AI 相关交互的开发者工具。
- 通过社区插件支持来自 Google AI、Vertex AI 以及第三方的多种大语言模型。

### 选择正确的工具

最终，最佳选择取决于项目的具体目标。如果你在一个定义良好的框架内构建复杂、协作的智能体系统，ADK 提供了强大的方案。对于许多需要灵活性和广泛模型支持的其他 GenAI 项目，Genkit 是出色的选择。

## ADK 可在任何地方工作，但针对 Google Cloud 做了优化

虽然 Agent Development Kit（ADK）提供与各种工具一起工作的灵活性，但它针对在 Google Cloud 生态系统内、特别是与 Gemini 模型和 Vertex AI 的无缝集成做了优化。这种量身设计让开发者能充分利用 Gemini 的高级能力，例如 Gemini 2.5 Pro Experimental 中增强的推理和工具使用，并提供把这些智能体部署到 Vertex AI 完全托管、企业级运行时以实现可扩展性的直接、原生路径。

至关重要的是，这种深度集成延伸到更广泛的企业版图；ADK 使智能体能够通过 100 多个预构建连接器直接连接到系统和数据，利用用 Application Integration 构建的工作流，并访问存储在 AlloyDB、BigQuery 和 NetApp 等系统中的数据，而无需数据复制。

此外，用 ADK 构建的智能体可以安全地利用通过 Apigee 管理的组织现有 API 投资，进一步通过已建立的接口增强其能力。

这种跨越先进 AI 模型、可扩展部署、多样数据源和现有 API 的全面连通性，使 ADK 在 Google Cloud 环境中使用时格外强大。

## 用 ADK 构建下一代智能体

Agent Development Kit（ADK）为构建下一代 AI 应用提供了强大、灵活且开源的基础。它通过以下方式应对多智能体开发的核心挑战：

- 对智能体行为与编排的精确控制。
- 丰富的工具与集成生态。
- 用于构建和调试的集成开发者体验。
- 对可靠智能体至关重要的稳健评估框架。
- 包括托管选项在内的清晰部署路径。

我们非常兴奋地期待看到你用 ADK 构建的东西。
