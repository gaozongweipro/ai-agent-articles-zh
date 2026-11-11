---
title_en: Equipping agents for the real world with Agent Skills
title_zh: 用 Agent Skills 为智能体配备真实世界能力
company: anthropic
date: 2025-10-16
updated: 2025-12-18
url: https://www.anthropic.com/research/equipping-agents-for-the-real-world-with-agent-skills
type: full
category: 工具与协议
tags:
  - Agent Skills
  - Skills
  - 工具调用
  - MCP
---

# 用 Agent Skills 为智能体配备真实世界能力

- Dec 18, 2025

  ### 更新

  我们已将 Agent Skills 作为开放标准发布，以支持跨平台可移植性。

  [查看更多](https://agentskills.io/)

---

随着模型能力提升，我们现在可以构建与完整计算环境交互的通用智能体。例如，[Claude Code](https://claude.com/product/claude-code) 可以通过本地代码执行和文件系统，跨领域完成复杂任务。但随着这些智能体变得更强大，我们需要更可组合、可扩展、可移植的方式，为它们配备领域专长。

这促使我们创建了 [**Agent Skills**](https://www.anthropic.com/news/skills)：由指令、脚本和资源组成的有组织文件夹，智能体可以动态发现并加载它们，以在特定任务上表现更好。Skills 把你的专长打包成可供 Claude 组合使用的资源，从而扩展 Claude 的能力，把通用智能体转变为适合你需求的专门智能体。

为智能体构建一项 skill，就像为新员工准备一份入职指南。不必再为每个用例构建零散、定制的智能体；任何人现在都可以通过捕捉并分享程序性知识，用可组合的能力来特化自己的智能体。本文将说明 Skills 是什么、如何工作，并分享构建自己的 Skills 的最佳实践。

一项 skill 是一个包含 `SKILL.md` 文件的目录，其中还有为智能体提供额外能力的、有组织的指令、脚本和资源文件夹。

## 一项 skill 的解剖结构

为了看清 Skills 的实际运作，我们来看一个真实例子：支撑 [Claude 近期推出的文档编辑能力](https://www.anthropic.com/news/create-files) 的一项 skill。Claude 已经很擅长理解 PDF，但直接操作它们的能力有限（例如填写表单）。这个 [PDF skill](https://github.com/anthropics/skills/tree/main/document-skills/pdf) 让我们能赋予 Claude 这些新能力。

最简单的 skill 就是一个包含 `SKILL.md` 文件的目录。该文件必须以 YAML frontmatter 开头，其中包含一些必需的元数据：`name` 和 `description`。启动时，智能体会把每个已安装 skill 的 `name` 和 `description` 预加载到其 system prompt 中。

这些元数据是 *progressive disclosure（渐进式披露）* 的**第一层**：它只提供刚好足够的信息，让 Claude 知道何时该使用每项 skill，而不必把全部内容加载进 context。该文件的正文是**第二层**细节。如果 Claude 认为这项 skill 与当前任务相关，它会读取完整的 `SKILL.md` 并将其加载进 context。

`SKILL.md` 文件必须以包含文件名和描述的 YAML Frontmatter 开头，这些内容会在启动时被加载进 system prompt。

随着 skills 变得更复杂，它们可能包含太多无法放入单个 `SKILL.md` 的 context，或只在特定场景下才相关的 context。这时，skills 可以在 skill 目录中捆绑额外文件，并在 `SKILL.md` 中按名称引用它们。这些额外的链接文件是**第三层**（及更深层）细节，Claude 可以按需选择浏览和发现。

在下面展示的 PDF skill 中，`SKILL.md` 引用了作者选择与核心 `SKILL.md` 一起捆绑的两个额外文件（`reference.md` 和 `forms.md`）。通过把填表说明移到单独的文件（`forms.md`），作者可以保持 skill 核心部分精简，并相信 Claude 只在填写表单时才会去读 `forms.md`。

你可以把更多 context（通过额外文件）纳入 skill，随后由 Claude 根据 system prompt 触发。

Progressive disclosure 是使 Agent Skills 灵活且可扩展的核心设计原则。就像一本组织良好的手册：先是目录，然后是具体章节，最后是详细附录，skills 让 Claude 只在需要时加载信息。

拥有文件系统和代码执行工具的智能体，在处理某项任务时不必把整项 skill 全部读进 context window。这意味着可以捆绑进一项 skill 的 context 量实际上是没有上限的。

### Skills 与 context window

下图展示了当用户消息触发一项 skill 时，context window 如何变化。

Skills 通过你的 system prompt 在 context window 中被触发。

所示操作序列：

1. 一开始，context window 中有核心 system prompt、每个已安装 skill 的元数据，以及用户的初始消息；
2. Claude 通过调用 Bash 工具读取 `pdf/SKILL.md` 的内容，从而触发 PDF skill；
3. Claude 选择读取与该 skill 捆绑的 `forms.md` 文件；
4. 最后，Claude 在从 PDF skill 加载了相关指令后，继续处理用户的任务。

### Skills 与代码执行

Skills 也可以包含代码，供 Claude 酌情作为工具来执行。

大语言模型擅长许多任务，但某些操作更适合用传统代码执行。例如，通过生成 token 来排序一个列表，远比直接运行排序算法更昂贵。除了效率问题，许多应用还需要只有代码才能提供的确定性可靠性。

在我们的例子中，PDF skill 包含一个预先写好的 Python 脚本，用于读取 PDF 并提取所有表单字段。Claude 可以运行这个脚本，而不必把脚本或 PDF 加载进 context。并且因为代码是确定性的，这一工作流是一致且可重复的。

Skills 也可以包含代码，供 Claude 根据任务性质酌情作为工具执行。

## 开发与评估 skills

以下是开始撰写和测试 skills 时的一些有用指南：

- **从评估开始：** 让智能体在有代表性的任务上运行，观察它们在何处遇到困难或需要额外 context，从而找出能力缺口。然后逐步构建 skills 来弥补这些不足。
- **为规模化做好结构：** 当 `SKILL.md` 变得臃肿时，把它的内容拆到单独文件并加以引用。如果某些 context 互斥或很少一起使用，保持路径分离将减少 token 用量。最后，代码既可以充当可执行工具，也可以充当文档。应当明确：Claude 是该直接运行脚本，还是把它们作为参考读进 context。
- **从 Claude 的视角思考：** 观察 Claude 在真实场景中如何使用你的 skill，并根据观察进行迭代：留意意外的轨迹，或对某些 context 的过度依赖。特别注意 skill 的 `name` 和 `description`。Claude 会根据它们来决定是否针对当前任务触发该 skill。
- **与 Claude 一起迭代：** 在与 Claude 一起做任务时，请它把成功的方法和常见错误沉淀为 skill 中可复用的 context 和代码。如果它在使用某项 skill 完成任务时偏离正轨，请它自我反思哪里出了问题。这一过程能帮你发现 Claude 真正需要的 context，而不是事先去猜测。

### 使用 Skills 时的安全考虑

Skills 通过指令和代码为 Claude 提供新能力。这使它们很强大，但也意味着恶意 skills 可能在使用环境中引入漏洞，或引导 Claude 泄密并采取非预期行动。

我们建议只从可信来源安装 skills。从不太可信的来源安装时，使用前务必彻底审计。首先阅读 skill 中捆绑的文件内容以理解它做什么，尤其注意代码依赖，以及图像或脚本等捆绑资源。同样，留意 skill 中指示 Claude 连接可能不受信任的外部网络来源的指令或代码。

## Skills 的未来

Agent Skills 目前已在 [Claude.ai](http://claude.ai)、Claude Code、Claude Agent SDK 以及 Claude Developer Platform 上得到[支持](https://www.anthropic.com/news/skills)。

在接下来的几周里，我们将继续增加支持 Skills 全生命周期的功能：创建、编辑、发现、分享和使用。我们尤其期待 Skills 帮助组织和个人与 Claude 分享他们的 context 和工作流。我们也将探索 Skills 如何通过教导智能体涉及外部工具和软件的更复杂工作流，来补充 [Model Context Protocol](https://modelcontextprotocol.io/)（MCP）服务器。

再往前看，我们希望让智能体能够自己创建、编辑和评估 Skills，把它们自己的行为模式编码为可复用的能力。

Skills 是一个简单的概念，格式也同样简单。这种简单性使组织、开发者和最终用户更容易构建定制智能体，并赋予它们新能力。

我们很期待看到人们用 Skills 构建出什么。今天就可以从我们的 Skills [文档](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview)和 [cookbook](https://github.com/anthropics/claude-cookbooks/tree/main/skills) 开始。

## 作者与致谢

### 致谢

由 Barry Zhang、Keith Lazuka 和 Mahesh Murag 撰写，他们都非常喜欢文件夹。特别感谢 Anthropic 内部许多倡导、支持和构建 Skills 的同事。
