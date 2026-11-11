---
title_en: New tools for building agents
title_zh: 构建智能体的新工具
company: openai
date: 2025-03-11
url: https://openai.com/index/new-tools-for-building-agents/
type: full
category: 框架与 SDK
tags:
  - Agents SDK
  - Responses API
  - Computer Use
  - 工具调用
  - 多 Agent
---

# 构建智能体的新工具

今天，我们发布第一组构建块，帮助开发者与企业构建有用且可靠的智能体。我们把智能体视为代表用户独立完成任务的系统。过去一年，我们引入了新的模型能力——例如高级推理、多模态交互和新的安全技术——为模型处理构建智能体所需的复杂多步任务奠定了基础。然而，客户反馈，把这些能力变成可投产的智能体往往很有挑战，常常需要大量提示迭代和定制编排逻辑，却没有足够的可见性或内置支持。

为应对这些挑战，我们推出一组专门为简化智能体应用开发而设计的新 API 与工具：

- 新的 Responses API，把 Chat Completions API 的简洁性与 Assistants API 的工具使用能力结合起来，用于构建智能体
- 内置工具，包括网络搜索、文件搜索和计算机使用
- 新的 Agents SDK，用于编排单智能体和多智能体工作流
- 集成的可观测性工具，用于追踪和检查智能体工作流执行

这些新工具简化了核心智能体逻辑、编排和交互，使开发者开始构建智能体显著更容易。在随后数周和数月中，我们计划发布更多工具和能力，进一步简化和加速在我们平台上构建智能体应用。

## 介绍 Responses API

Responses API 是我们用于借助 OpenAI 内置工具构建智能体的新 API 原语。它结合了 Chat Completions 的简洁性与 Assistants API 的工具使用能力。随着模型能力继续演进，我们相信 Responses API 将为构建智能体应用的开发者提供更灵活的基础。通过一次 Responses API 调用，开发者将能够使用多种工具和模型轮次解决日益复杂的任务。

一开始，Responses API 将支持网络搜索、文件搜索和计算机使用等新的内置工具。这些工具被设计为协同工作，把模型连接到真实世界，使它们在完成任务时更有用。它还带来若干可用性改进，包括统一的基于 item 的设计、更简单的多态、直观的流式事件，以及像 `response.output_text` 这样可轻松访问模型文本输出的 SDK 辅助方法。

Responses API 面向希望轻松把 OpenAI 模型与内置工具结合进应用、而不想集成多个 API 或外部供应商之复杂性的开发者。该 API 也更容易把数据存储在 OpenAI 上，以便开发者使用追踪和评估等功能来评估智能体表现。提醒一下，即使数据存储在 OpenAI 上，我们默认也不会用企业数据训练模型。该 API 即日起向所有开发者提供，不单独收费——tokens 和工具按定价页上的标准费率计费。更多信息见 Responses API 快速入门指南。

## 这对现有 API 意味着什么

- Chat Completions API：Chat Completions 仍是我们采用最广泛的 API，我们完全致力于用新模型和能力支持它。不需要内置工具的开发者可以放心地继续使用 Chat Completions。只要新模型的能力不依赖于内置工具或多次模型调用，我们就会继续向 Chat Completions 发布新模型。不过，Responses API 是具有同样出色性能的 Chat Completions 超集，因此对于新集成，我们建议从 Responses API 开始。
- Assistants API：基于 Assistants API 测试中的开发者反馈，我们把关键改进纳入了 Responses API，使其更灵活、更快、更易用。我们正在努力实现 Assistants 与 Responses API 之间的完整功能对等，包括对类似 Assistant 和 Thread 的对象以及 Code Interpreter 工具的支持。完成后，我们计划正式宣布 Assistants API 弃用，目标日落日期在 2026 年中。弃用时，我们将提供从 Assistants API 到 Responses API 的清晰迁移指南，使开发者能够保留所有数据并迁移应用。在正式宣布弃用之前，我们将继续向 Assistants API 交付新模型。Responses API 代表在 OpenAI 上构建智能体的未来方向。

## 在 Responses API 中引入内置工具

开发者现在可以从网络获得带有清晰、相关引用的快速、最新答案。在 Responses API 中，当使用 gpt-4o 和 gpt-4o-mini 时，网络搜索可作为工具使用，并可与其他工具或函数调用配对。

```javascript
const response = await openai.responses.create({
  model: "gpt-4o",
  tools: [{ type: "web_search_preview" }],
  input: "What was a positive news story that happened today?",
});
console.log(response.output_text);
```

在早期测试中，我们看到开发者把网络搜索用于购物助手、研究智能体和旅行预订智能体等多种用例——任何需要来自网络之及时信息的应用。

例如，Hebbia 利用网络搜索工具，帮助资产管理、私募股权和信贷公司以及律师事务所，从大量公共和私有数据集中快速提取可执行洞察。通过把实时搜索能力集成进研究工作流，Hebbia 提供更丰富、特定于上下文的市场情报，并持续提高分析的精确性与相关性，优于当前基准。

API 中的网络搜索由与 ChatGPT 搜索相同的模型提供动力。在评估 LLM 回答简短事实问题准确性的 SimpleQA 基准上，GPT-4o search preview 和 GPT-4o mini search preview 分别得到 90% 和 88%。

用 API 中的网络搜索生成的回复包含指向新闻文章和博客等来源的链接，让用户有途径了解更多。凭借这些清晰的行内引用，用户能以新的方式与信息互动，内容所有者则获得触及更广泛受众的新机会。任何网站或出版商都可以选择出现在 API 的网络搜索中。

网络搜索工具以预览形式在 Responses API 中向所有开发者提供。我们也通过 `gpt-4o-search-preview` 和 `gpt-4o-mini-search-preview`，在 Chat Completions API 中向开发者直接提供微调后的搜索模型。定价分别从每千次查询 30 美元和 25 美元起。可在 Playground 中试用，并在文档中了解更多。

## 文件搜索

开发者现在可以更轻松地用改进后的文件搜索工具，从大量文档中检索相关信息。它支持多种文件类型、查询优化、元数据过滤和自定义重排序，能够提供快速、准确的搜索结果。同样，在 Responses API 中只需几行代码即可集成。

```javascript
const productDocs = await openai.vectorStores.create({
  name: "Product Documentation",
  file_ids: [file1.id, file2.id, file3.id],
});
const response = await openai.responses.create({
  model: "gpt-4o-mini",
  tools: [{
    type: "file_search",
    vector_store_ids: [productDocs.id],
  }],
  input: "What is deep research by OpenAI?",
});
console.log(response.output_text);
```

文件搜索工具可用于多种真实用例，包括让客户支持智能体轻松访问 FAQ，帮助法律助理为合格专业人士快速参考过往案件，以及协助编码智能体查询技术文档。例如，Navan 在其 AI 驱动的旅行智能体中使用文件搜索，快速从知识库文章（如公司差旅政策）中为用户提供精确答案。凭借内置的查询优化和重排序，他们无需额外调优或配置即可建立强大的 RAG 流水线。通过为每个用户组配备专用向量存储，Navan 能够根据账户设置和用户角色定制答案，为客户和员工节省时间，同时帮助提供准确、个性化的支持。

该工具在 Responses API 中向所有开发者提供。使用定价为每千次查询 2.50 美元，文件存储为每 GB 每天 0.10 美元，首 GB 免费。该工具在 Assistants API 中继续可用。最后，我们还为 Vector Store API 对象添加了新的搜索端点，以便直接查询数据供其他应用和 API 使用。详见文档并可在 Playground 中开始测试。

## 计算机使用

为构建能在计算机上完成任务的智能体，开发者现在可以在 Responses API 中使用计算机使用工具，它由为 Operator 提供动力的同一 Computer-Using Agent（CUA）模型驱动。这一研究预览模型刷新了领先纪录：在 OSWorld 的完整计算机使用任务上达到 38.1%，在 WebArena 上达到 58.1%，在 WebVoyager 的基于网页交互上达到 87%。

内置的计算机使用工具捕获模型生成的鼠标和键盘动作，使开发者能通过直接把这些动作翻译成其环境中的可执行命令，来自动化计算机使用任务。

```javascript
const response = await openai.responses.create({
  model: "computer-use-preview",
  tools: [{
    type: "computer_use_preview",
    display_width: 1024,
    display_height: 768,
    environment: "browser",
  }],
  truncation: "auto",
  input: "I'm looking for a new camera. Help me find the best one.",
});
console.log(response.output);
```

开发者可以用计算机使用工具自动化基于浏览器的工作流，例如对 Web 应用进行质量保证，或在遗留系统中执行数据录入。例如，Unify 是一套用于增长收入的行动系统，用智能体识别意向、研究客户并与买家互动。借助 OpenAI 的计算机使用工具，Unify 的智能体可以访问以前无法通过 API 获得的信息——例如让物业管理公司通过在线地图验证一家企业是否扩大了不动产足迹。这种研究作为一种自定义信号，触发个性化外联，帮助 go-to-market 团队精确而规模化地接触买家。

再如，Luminai 集成计算机使用工具，为缺少 API 可用性和标准化数据的大型企业遗留系统自动化复杂运营工作流。在与一家大型社区服务组织的近期试点中，Luminai 仅用数天就自动化了申请处理和用户注册——传统机器人流程自动化（RPA）经过数月努力仍难以实现。

在去年于 Operator 中推出 CUA 之前，我们进行了广泛的安全测试和红队演练，覆盖三类关键风险：滥用、模型错误和前沿风险。为应对通过 API 中的 CUA 把 Operator 能力扩展到本地操作系统所带来的风险，我们进行了额外的安全评估和红队演练。我们还为开发者增加了缓解措施，包括防御提示注入的安全检查、敏感任务的确认提示、帮助开发者隔离环境的工具，以及对潜在政策违规的增强检测。尽管这些缓解有助于降低风险，模型仍可能出现非故意错误，尤其是在非浏览器环境中。例如，CUA 在旨在衡量 AI 智能体在真实任务上表现的 OSWorld 上目前为 38.1%，表明该模型在自动化操作系统任务上尚不够高度可靠。在这些场景中建议有人工监督。关于针对 API 的安全工作的更多细节，见更新后的系统卡。原文提供了与此前 SOTA 和人类表现对比的基准表。

即日起，计算机使用工具作为研究预览，在 Responses API 中向使用层级 3–5 的选定开发者提供。定价为每 100 万输入 tokens 3 美元、每 100 万输出 tokens 12 美元。详见文档，并查看说明如何用该工具构建的示例应用。

## Agents SDK

除了构建智能体的核心逻辑并给它们访问工具的能力以使它们有用之外，开发者还需要编排智能体工作流。我们新的开源 Agents SDK 简化了多智能体工作流的编排，并相对我们去年发布、被开发者社区广泛采用且被多家客户成功部署的实验性 SDK Swarm，提供了显著改进。

改进包括：

- 智能体：易于配置的 LLM，具有清晰指令和内置工具。
- 交接（Handoffs）：在智能体之间智能地转移控制权。
- 护栏（Guardrails）：用于输入和输出验证的可配置安全检查。
- 追踪与可观测性：可视化智能体执行轨迹，以便调试和优化性能。

```python
from agents import Agent, Runner, WebSearchTool, function_tool, guardrail

support_agent = Agent(
    name="Support & Returns",
    instructions="You are a support agent who can submit refunds [...]",
)
shopping_agent = Agent(
    name="Shopping Assistant",
    tools=[WebSearchTool()],
)
triage_agent = Agent(
    name="Triage Agent",
    instructions="Route the user to the correct agent.",
    handoffs=[shopping_agent, support_agent],
)
output = Runner.run_sync(
    starting_agent=triage_agent,
    input="What shoes might work best with my outfit so far?",
)
```

Agents SDK 适用于各种真实应用，包括客户支持自动化、多步研究、内容生成、代码审查和销售开拓。例如，Coinbase 用 Agents SDK 快速原型化并部署了 AgentKit，这是一个让 AI 智能体与加密钱包和各种链上活动无缝交互的工具包。仅用几个小时，Coinbase 就把 Developer Platform SDK 中的自定义动作集成进一个功能完整的智能体。AgentKit 的精简架构简化了添加新智能体动作的过程，让开发者更能专注于有意义的集成，而更少花时间在复杂的智能体设置上。

几天之内，Box 就能快速创建利用网络搜索和 Agents SDK 的智能体，使企业能够搜索、查询并从其在 Box 中存储的非结构化数据以及公共互联网来源中提取洞察。这种方法让客户不仅能获取最新信息，还能以遵守内部权限和安全政策的安全方式搜索其内部专有数据。例如，金融服务公司可以构建自定义智能体，调用 Box AI 智能体，将其存储在 Box 中的内部市场分析与来自网络的实时新闻和经济数据结合起来，为分析师提供用于投资决策的全面视图。

Agents SDK 可与 Responses API 和 Chat Completions API 一起工作。只要其他提供商提供 Chat Completions 风格的 API 端点，该 SDK 也可与它们的模型一起工作。开发者可以立即把它集成进 Python 代码库，Node.js 支持即将到来。详见文档。

在设计 Agents SDK 时，我们的团队受到社区中包括 Pydantic、Griffe 和 MkDocs 在内的优秀工作的启发。我们致力于继续把 Agents SDK 作为开源框架来构建，以便社区中的其他人可以扩展我们的方法。

## 下一步：构建智能体平台

我们相信智能体很快会成为劳动力中不可或缺的一部分，显著提高各行业的生产力。随着公司日益寻求利用 AI 处理复杂任务，我们致力于提供构建块，使开发者与企业能够有效创建交付真实世界影响的自主系统。

随着今天的发布，我们引入第一组构建块，赋能开发者与企业更轻松地构建、部署和扩展可靠、高性能的 AI 智能体。随着模型能力变得越来越具有智能体特性，我们将继续投资于跨 API 的更深集成，以及帮助在生产中部署、评估和优化智能体的新工具。我们的目标是给开发者一个无缝的平台体验，以构建可帮助完成任何行业中各种任务的智能体。我们兴奋地期待开发者接下来的构建。要开始，请探索我们的文档，并关注更多即将到来的更新。
