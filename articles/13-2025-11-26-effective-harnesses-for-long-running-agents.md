# 为长时运行智能体设计有效的 Harness

- 英文标题：Effective harnesses for long-running agents
- 中文标题：为长时运行智能体设计有效的 Harness
- 发布日期：2025-11-26
- 原文链接：https://www.anthropic.com/research/effective-harnesses-for-long-running-agents
- 翻译类型：全文翻译

---

随着 AI 智能体能力增强，开发者越来越多地要求它们承担需要数小时甚至数天的复杂任务。然而，让智能体在多个 context window 之间持续取得一致进展，仍是一个开放问题。

长时运行智能体的核心挑战是：它们必须在离散的会话中工作，而每个新会话开始时对之前发生的事情没有任何记忆。想象一个由轮班工程师组成的软件项目，每位新工程师到岗时都不记得上一班发生了什么。因为 context window 有限，而且大多数复杂项目无法在单个窗口内完成，智能体需要一种方法来弥合编程会话之间的鸿沟。

我们开发了一套双管齐下的方案，使 [Claude Agent SDK](https://platform.claude.com/docs/en/agent-sdk/overview) 能够跨许多 context window 有效工作：一个在首次运行时搭建环境的 **initializer agent（初始化智能体）**，以及一个在每个会话中负责任增量进展、同时为下一会话留下清晰产物的 **coding agent（编程智能体）**。代码示例见配套的 [quickstart](https://github.com/anthropics/claude-quickstarts/tree/main/autonomous-coding)。

## 长时运行智能体问题

Claude Agent SDK 是一个强大的通用智能体 harness，既擅长编程，也擅长其他需要模型使用工具来收集 context、规划并执行的任务。它具有 compaction（压缩）等 context 管理能力，使智能体可以在不耗尽 context window 的情况下持续工作。从理论上说，有了这套设置，智能体应当可以任意长时间地持续做有用的工作。

然而，仅有 compaction 并不够。开箱即用时，即使是像 Opus 4.5 这样的前沿编程模型，在 Claude Agent SDK 上跨多个 context window 循环运行，如果只得到一个高层 prompt（例如 “做一个 [claude.ai](http://claude.ai) 的克隆”），也仍然难以构建出生产质量的 web 应用。

Claude 的失败表现为两种模式。第一，智能体倾向于一次做得太多——本质上试图 one-shot 整个应用。这常常导致模型在实现中途耗尽 context，给下一会话留下一个实现到一半、且没有文档的功能。智能体随后只能猜测之前发生了什么，并花大量时间试图让基础应用重新跑起来。即使有 compaction，这种情况仍会发生，因为它并不总是能向下一个智能体传递完全清晰的指令。

第二种失败模式往往出现在项目后期。在一些功能已经完成后，后面的智能体实例环顾四周，看到已经有了进展，就宣布任务完成。

这把问题分解成两部分。首先，我们需要建立一个初始环境，为给定 prompt 所需的*所有*功能打下基础，从而让智能体可以一步一步、一个功能一个功能地工作。其次，我们应提示每个智能体在朝着目标做增量进展的同时，在会话结束时把环境留在干净状态。所谓 “干净状态”，是指适合合并到 main 分支的那种代码：没有重大 bug，代码整齐且文档良好，总体上，开发者可以轻松开始做新功能，而不必先去清理一堆无关的烂摊子。

在内部实验中，我们用一套两部分的方案来解决这些问题：

1. Initializer agent：最第一个智能体会话使用专门的 prompt，要求模型搭建初始环境：一个 `init.sh` 脚本、一个记录智能体已做事项的 `claude-progress.txt` 文件，以及一次展示新增文件的初始 git commit。
2. Coding agent：之后的每个会话都要求模型做增量进展，然后留下结构化更新。[^1]

这里的关键洞见是：找到一种方法，让智能体在带着全新 context window 开始时，能迅速理解工作状态。这由 `claude-progress.txt` 文件与 git 历史共同完成。这些做法的灵感来自高效软件工程师每天在做的事情。

## 环境管理

在更新后的 [Claude 4 prompting guide](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices#multi-context-window-workflows) 中，我们分享了多 context window 工作流的一些最佳实践，包括一种 “为最第一个 context window 使用不同 prompt” 的 harness 结构。这个 “不同的 prompt” 要求 initializer agent 用未来 coding agents 有效工作所需的全部必要 context 来搭建环境。这里，我们更深入地介绍这一环境的一些关键组成部分。

### 功能列表（Feature list）

为了解决智能体 one-shot 整个应用、或过早认为项目已经完成的问题，我们提示 initializer agent 根据用户的初始 prompt，写出一份全面的功能需求文件。在 [claude.ai](http://claude.ai) 克隆的例子中，这意味着超过 200 项功能，例如 “用户可以打开新对话、输入查询、按回车，并看到 AI 回复”。这些功能最初全部被标记为 “failing”，以便后来的 coding agents 对完整功能应该是什么样子有清晰的纲要。

```plaintext
{
    "category": "functional",
    "description": "New chat button creates a fresh conversation",
    "steps": [
      "Navigate to main interface",
      "Click the 'New Chat' button",
      "Verify a new conversation is created",
      "Check that chat area shows welcome state",
      "Verify conversation appears in sidebar"
    ],
    "passes": false
  }
```

我们提示 coding agents 编辑这个文件时只能改 `passes` 字段的状态，并用措辞强硬的指令，例如 “删除或编辑测试是不可接受的，因为这可能导致功能缺失或存在 bug。” 经过一些实验后，我们决定使用 JSON，因为与 Markdown 文件相比，模型不太会不适当地改动或覆盖 JSON 文件。

### 增量进展

有了这套初始环境脚手架后，下一轮的 coding agent 被要求一次只做一项功能。这种增量方法被证明对解决智能体一次做得太多的倾向至关重要。

一旦开始增量工作，模型在做出代码改动后仍必须把环境留在干净状态。在实验中，我们发现引出这种行为的最佳方式，是要求模型用描述性的 commit message 把进展提交到 git，并在进度文件中写下进展摘要。这使模型可以用 git 回退糟糕的代码改动，并恢复代码库的可用状态。

这些方法也提高了效率，因为智能体不必再猜测之前发生了什么，也不必把时间花在让基础应用重新跑起来上。

### 测试

我们观察到的另一个主要失败模式是：Claude 倾向于在没有适当测试的情况下把功能标为完成。如果没有明确提示，Claude 往往会改代码，甚至用单元测试或针对开发服务器的 `curl` 命令做测试，但却认识不到该功能并没有端到端地工作。

在构建 web 应用的例子中，一旦被明确提示使用浏览器自动化工具、并像人类用户那样做全部测试，Claude 在端到端验证功能上大多表现良好。

Claude 通过 Puppeteer MCP server 测试 claude.ai 克隆时拍摄的截图。

为 Claude 提供这类测试工具显著改善了表现，因为智能体能够发现并修复仅从代码本身并不明显的 bug。

仍有一些问题存在，例如 Claude 的视觉能力以及浏览器自动化工具的限制，使它难以识别每一种 bug。例如，Claude 无法通过 Puppeteer MCP 看到浏览器原生的 alert 模态框，因此依赖这些模态框的功能往往更容易出 bug。

## 进入状态

有了以上全部设置后，每个 coding agent 都被提示先执行一系列步骤来认清形势，其中有些相当基本，但仍然有帮助：

1. *运行 `pwd`，看看你正在哪个目录工作。你将只能编辑这个目录中的文件。*
2. *阅读 git 日志和进度文件，了解最近做了什么。*
3. *阅读功能列表文件，选择尚未完成的、优先级最高的功能开始做。*

这种方法为 Claude 在每个会话中节省了一些 token，因为它不必再去弄清楚如何测试代码。让 initializer agent 写一个可以运行开发服务器的 `init.sh` 脚本，并在实现新功能之前先跑一遍基本的端到端测试，也很有帮助。

在 claude.ai 克隆的例子中，这意味着智能体总会先启动本地开发服务器，并用 Puppeteer MCP 开始一个新对话、发送一条消息并收到回复。这确保 Claude 能迅速识别应用是否被留在损坏状态，并立即修复已有 bug。如果智能体直接开始实现新功能，问题往往会变得更糟。

综合以上，一个典型会话会以下面这些 assistant 消息开始：

```plaintext
[Assistant] I'll start by getting my bearings and understanding the current state of the project.
[Tool Use] <bash - pwd>
[Tool Use] <read - claude-progress.txt>
[Tool Use] <read - feature_list.json>
[Assistant] Let me check the git log to see recent work.
[Tool Use] <bash - git log --oneline -20>
[Assistant] Now let me check if there's an init.sh script to restart the servers.
<Starts the development server>
[Assistant] Excellent! Now let me navigate to the application and verify that some fundamental features are still working.
<Tests basic functionality>
[Assistant] Based on my verification testing, I can see that the fundamental functionality is working well. The core chat features, theme switching, conversation loading, and error handling are all functioning correctly. Now let me review the tests.json file more comprehensively to understand what needs to be implemented next.
<Starts work on a new feature>
```

## 智能体失败模式与解决方案

| 问题 | Initializer Agent 的行为 | Coding Agent 的行为 |
| --- | --- | --- |
| Claude 过早宣布整个项目已经完成。 | 根据输入规格建立功能列表文件：用结构化 JSON 列出端到端功能描述。 | 在会话开始时阅读功能列表文件。选择单一功能开始做。 |
| Claude 把环境留在有 bug 或进展未记录的状态。 | 写入初始 git 仓库和进度说明文件。 | 通过阅读进度说明和 git commit 日志开始会话，并在开发服务器上跑基本测试以捕捉未记录的 bug。以写入 git commit 和进度更新来结束会话。 |
| Claude 过早把功能标为完成。 | 建立功能列表文件。 | 对所有功能做自我验证。只有在仔细测试之后才把功能标为 “passing”。 |
| Claude 必须花时间弄清楚如何运行应用。 | 编写可运行开发服务器的 `init.sh` 脚本。 | 通过阅读 `init.sh` 开始会话。 |

上表总结了长时运行 AI 智能体中四种常见失败模式及其解决方案。

## 未来工作

这项研究展示了长时运行智能体 harness 中的一套可能方案，使模型能跨许多 context window 做增量进展。但仍有开放问题。

最值得注意的是，目前仍不清楚：一个通用的编程智能体在各种 context 中是否表现最好，还是通过多智能体架构能取得更好表现。看起来合理的是，像测试智能体、质量保证智能体或代码清理智能体这样的专门智能体，或许能在软件开发生命周期的子任务上做得更好。

此外，这个 demo 针对的是全栈 web 应用开发。未来方向是把这些发现推广到其他领域。这些经验中的部分或全部，很可能也适用于例如科学研究或金融建模所需的那类长时运行智能体任务。

## 脚注

[^1]: 我们在此语境中把它们称为不同的智能体，仅仅是因为它们有不同的初始用户 prompt。System prompt、工具集以及整体的智能体 harness 在其他方面是相同的。

## 作者与致谢

### 致谢

由 Justin Young 撰写。特别感谢 David Hershey、Prithvi Rajasakeran、Jeremy Hadfield、Naia Bouscal、Michael Tingley、Jesse Mu、Jake Eaton、Marius Buleandara、Maggie Vo、Pedram Navid、Nadine Yasser 和 Alex Notov 的贡献。

这项工作反映了 Anthropic 多个团队的共同努力，他们使 Claude 能够安全地从事长周期自主软件工程，尤其是 code RL 与 Claude Code 团队。有兴趣贡献的候选人欢迎在 [anthropic.com/careers](http://anthropic.com/careers) 申请。
