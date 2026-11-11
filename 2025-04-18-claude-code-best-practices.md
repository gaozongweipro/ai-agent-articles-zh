# Claude Code：智能体式编程最佳实践

- 英文标题：Claude Code: Best practices for agentic coding
- 中文标题：Claude Code：智能体式编程最佳实践
- 发布日期：2025-04-18
- 更新日期：2026-01-26（官方说明本文已不再维护，最新实践见 https://code.claude.com/docs/en/best-practices）
- 原文链接：https://www.anthropic.com/research/claude-code-best-practices
- 翻译类型：全文翻译

---

### Claude Code 最佳实践已迁移到文档（2026 年 1 月 26 日）

本博文已不再维护。关于最新的 Claude Code 最佳实践，请参阅官方文档（https://code.claude.com/docs/en/best-practices），该文档会随着 Claude Code 的演化保持更新。

---

我们最近[发布了 Claude Code](https://www.anthropic.com/news/claude-3-7-sonnet)，一个用于智能体式编程的命令行工具。作为研究项目开发的 Claude Code，为 Anthropic 的工程师和研究人员提供了一种更原生的方式，把 Claude 整合进他们的编程工作流。

Claude Code 有意保持底层、不过度主张，提供接近原始模型访问的能力，而不强迫特定工作流。这一设计哲学创造了一种灵活、可定制、可脚本化且安全的强大工具。尽管强大，这种灵活性也给刚接触智能体式编程工具的工程师带来了学习曲线——至少在他们形成自己的最佳实践之前是如此。

本文概述了已被证明有效的一般模式，既适用于 Anthropic 的内部团队，也适用于在各种代码库、语言和环境中使用 Claude Code 的外部工程师。这份清单中没有任何内容是一成不变或普遍适用的；把这些建议视为起点。我们鼓励你实验，并找到最适合自己的方法！

*需要更详细的信息？我们在 [claude.ai/code](https://claude.ai/code) 的综合文档涵盖了本文提到的全部功能，并提供额外示例、实现细节和高级技术。*

## 1. 定制你的设置

Claude Code 是一个会自动把 context 拉进 prompts 的智能体式编程助手。这种 context 收集会消耗时间和 tokens，但你可以通过环境调优来优化它。

### a. 创建 `CLAUDE.md` 文件

`CLAUDE.md` 是一个特殊文件，Claude 在开始对话时会自动把它拉进 context。这使它成为记录以下内容的理想位置：

- 常用 bash 命令
- 核心文件和工具函数
- 代码风格指南
- 测试说明
- 仓库礼仪（例如分支命名、merge vs. rebase 等）
- 开发者环境设置（例如 pyenv use、哪些编译器可用）
- 该项目特有的任何意外行为或警告
- 你希望 Claude 记住的其他信息

`CLAUDE.md` 文件没有必须的格式。我们建议保持简洁、人类可读。例如：

```plaintext
# Bash commands
- npm run build: Build the project
- npm run typecheck: Run the typechecker

# Code style
- Use ES modules (import/export) syntax, not CommonJS (require)
- Destructure imports when possible (eg. import { foo } from 'bar')

# Workflow
- Be sure to typecheck when you’re done making a series of code changes
- Prefer running single tests, and not the whole test suite, for performance
```

你可以把 `CLAUDE.md` 文件放在几个位置：

- **仓库根目录**，或你运行 `claude` 的位置（最常见的用法）。把它命名为 `CLAUDE.md` 并提交到 git，以便跨 sessions 并与团队共享（推荐），或命名为 `CLAUDE.local.md` 并把它加入 `.gitignore`
- **你运行 `claude` 的目录的任何父目录**。这对 monorepos 最有用：你可能从 `root/foo` 运行 `claude`，同时在 `root/CLAUDE.md` 和 `root/foo/CLAUDE.md` 中都有 `CLAUDE.md` 文件。这两者都会被自动拉进 context
- **你运行 `claude` 的目录的任何子目录**。这是上述情况的逆过程；在这种情形中，当你处理子目录中的文件时，Claude 会按需拉入 `CLAUDE.md` 文件
- **你的家目录**（`~/.claude/CLAUDE.md`），这会把它应用到你所有的 *claude* sessions

当你运行 `/init` 命令时，Claude 会自动为你生成一份 `CLAUDE.md`。

### b. 调优你的 `CLAUDE.md` 文件

你的 `CLAUDE.md` 文件会成为 Claude 的 prompts 的一部分，因此应当像任何经常使用的 prompt 一样被精炼。一个常见错误是加入大量内容，却不迭代其有效性。花时间实验，并确定什么能从模型那里产生最好的指令遵循。

你可以手动向 `CLAUDE.md` 添加内容，或按 `#` 键给 Claude 一条指令，它会自动把该指令纳入相关的 `CLAUDE.md`。许多工程师在编程时频繁使用 `#` 来记录命令、文件和风格指南，然后把 `CLAUDE.md` 的改动包含进 commits，使团队成员也能受益。

在 Anthropic，我们偶尔会把 `CLAUDE.md` 文件放到 [prompt improver](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/prompt-improver) 中运行，并常常调优指令（例如用 “IMPORTANT” 或 “YOU MUST” 增加强调）以提高遵守程度。

### c. 策划 Claude 的允许工具列表

默认情况下，Claude Code 会为任何可能修改你系统的动作请求许可：文件写入、许多 bash 命令、MCP 工具等。我们有意以这种保守方法设计 Claude Code，以优先考虑安全。你可以定制允许列表，许可你知道是安全的额外工具，或允许容易撤销的潜在不安全工具（例如文件编辑、`git commit`）。

管理允许工具有四种方式：

- 在 session 中被提示时**选择 “Always allow”**。
- 启动 Claude Code 后**使用 `/permissions` 命令**，从允许列表中添加或移除工具。例如，你可以添加 `Edit` 以始终允许文件编辑，添加 `Bash(git commit:*)` 以允许 git commits，或添加 `mcp__puppeteer__puppeteer_navigate` 以允许用 Puppeteer MCP server 导航。
- **手动编辑**你的 `.claude/settings.json` 或 `~/.claude.json`（我们建议把前者提交到源代码控制以与团队共享）。
- **使用 `--allowedTools` CLI 标志**来设置特定于 session 的权限。

### d. 如果使用 GitHub，安装 gh CLI

Claude 知道如何使用 `gh` CLI 与 GitHub 交互，以创建 issues、打开 pull requests、阅读评论等。如果没有安装 `gh`，Claude 仍然可以使用 GitHub API 或 MCP server（如果你已安装）。

## 2. 给 Claude 更多工具

Claude 可以访问你的 shell 环境，你可以像为自己一样，为它构建一套便利脚本和函数。它也可以通过 MCP 和 REST APIs 利用更复杂的工具。

### a. 把 Claude 与 bash 工具一起使用

Claude Code 继承你的 bash 环境，从而可以访问你的全部工具。虽然 Claude 知道 unix 工具和 `gh` 等常用实用程序，但如果没有说明，它不会知道你的定制 bash 工具：

1. 告诉 Claude 工具名称并附上使用示例
2. 告诉 Claude 运行 `--help` 以查看工具文档
3. 把经常使用的工具记录在 `CLAUDE.md` 中

### b. 把 Claude 与 MCP 一起使用

Claude Code 既可以作为 MCP server，也可以作为 client。作为 client，它可以通过三种方式连接到任意数量的 MCP servers 以访问它们的工具：

- **在项目配置中**（在该目录中运行 Claude Code 时可用）
- **在全局配置中**（在所有项目中可用）
- **在已提交的 `.mcp.json` 文件中**（对在你的代码库中工作的任何人都可用）。例如，你可以把 Puppeteer 和 Sentry servers 加入 `.mcp.json`，这样在你仓库上工作的每位工程师都可以开箱即用地使用它们。

在使用 MCP 时，用 `--mcp-debug` 标志启动 Claude 也有助于识别配置问题。

### c. 使用定制 slash commands

对于重复工作流——调试循环、日志分析等——把 prompt 模板存储在 `.claude/commands` 文件夹中的 Markdown 文件里。当你输入 `/` 时，这些会通过 slash commands 菜单变得可用。你可以把这些命令提交到 git，使它们对团队其他成员也可用。

定制 slash commands 可以包含特殊关键字 `$ARGUMENTS`，以便从命令调用中传递参数。

例如，下面是一个你可以用来自动拉取并修复 GitHub issue 的 slash command：

```plaintext
Please analyze and fix the GitHub issue: $ARGUMENTS.

Follow these steps:

1. Use `gh issue view` to get the issue details
2. Understand the problem described in the issue
3. Search the codebase for relevant files
4. Implement the necessary changes to fix the issue
5. Write and run tests to verify the fix
6. Ensure code passes linting and type checking
7. Create a descriptive commit message
8. Push and create a PR

Remember to use the GitHub CLI (`gh`) for all GitHub-related tasks.
```

把上述内容放入 `.claude/commands/fix-github-issue.md`，它就会作为 Claude Code 中的 `/project:fix-github-issue` 命令可用。然后你例如可以使用 `/project:fix-github-issue 1234` 让 Claude 修复 issue #1234。类似地，你可以把个人命令添加到 `~/.claude/commands` 文件夹，以便在所有 sessions 中都可用。

## 3. 尝试常见工作流

Claude Code 不强迫特定工作流，让你灵活地按自己想要的方式使用它。在这种灵活性所提供的空间中，我们的用户社区中已经出现了若干有效使用 Claude Code 的成功模式：

### a. 探索、规划、编码、提交

这一通用工作流适合许多问题：

1. **请 Claude 阅读相关文件、图像或 URL**，既可以给出一般指向（“阅读处理日志的文件”），也可以给出具体文件名（“阅读 logging.py”），但明确告诉它现在先不要写任何代码。

   1. 这是工作流中你应当考虑大力使用 subagents 的部分，尤其是对于复杂问题。告诉 Claude 使用 subagents 来核实细节或调查它可能有的特定问题——尤其是在对话或任务的早期——往往能在效率损失不大的情况下保留 context 可用性。
2. **请 Claude 制定如何处理特定问题的计划**。我们建议使用单词 “think” 来触发 extended thinking 模式，这给 Claude 额外的计算时间以更彻底地评估替代方案。这些特定短语被直接映射到系统中不断增加的思考预算：“think” < “think hard” < “think harder” < “ultrathink”。每一级都为 Claude 分配逐步更多的思考预算。

   1. 如果这一步的结果看起来合理，你可以让 Claude 用其计划创建一份文档或一个 GitHub issue，这样如果实现（步骤 3）不是你想要的，你可以重置到这一点。
3. **请 Claude 用代码实现其方案**。这也是一个好时机，请它在实现方案各部分时显式验证该方案的合理性。
4. **请 Claude 提交结果并创建 pull request**。如果相关，这也是让 Claude 用它所做事情的说明更新任何 README 或 changelog 的好时机。

步骤 #1–#2 至关重要——没有它们，Claude 往往会直接跳到编写解决方案。虽然有时那就是你想要的，但先请 Claude 研究和规划，会显著提高需要事先更深入思考的问题的表现。

### b. 写测试并提交；编码、迭代、提交

这是 Anthropic 钟爱的工作流，适用于可以用单元、集成或端到端测试轻松验证的改动。测试驱动开发（TDD）在智能体式编程中变得更加强大：

1. **请 Claude 基于期望的输入/输出对编写测试**。明确说明你在做测试驱动开发，这样它会避免创建 mock 实现，即使该功能在代码库中还不存在。
2. **告诉 Claude 运行测试并确认它们失败**。在这个阶段明确告诉它不要写任何实现代码通常会有帮助。
3. **在你对测试满意时，请 Claude 提交测试**。
4. **请 Claude 编写能通过测试的代码**，并指示它不要修改测试。告诉 Claude 一直继续直到全部测试通过。Claude 通常需要几次迭代来写代码、运行测试、调整代码，再运行测试。

   1. 在这个阶段，请它用独立的 subagents 验证实现没有过拟合到测试上，可能会有帮助
5. **在你对改动满意后，请 Claude 提交代码**。

当 Claude 有一个清晰的迭代目标——视觉稿、测试用例或另一种输出——时，它表现最好。通过提供像测试这样的期望输出，Claude 可以做出改动、评估结果，并增量改进直到成功。

### c. 写代码、截图结果、迭代

与测试工作流类似，你可以给 Claude 提供视觉目标：

1. **给 Claude 一种截取浏览器截图的方式**（例如使用 [Puppeteer MCP server](https://github.com/modelcontextprotocol/servers/tree/c19925b8f0f2815ad72b08d2368f0007c86eb8e6/src/puppeteer)、[iOS simulator MCP server](https://github.com/joshuayoes/ios-simulator-mcp)，或手动把截图复制/粘贴进 Claude）。
2. **通过复制/粘贴或拖放图像，或给 Claude 图像文件路径，给它一份视觉稿**。
3. **请 Claude 用代码实现设计**，对结果截图，并迭代直到其结果与稿件相符。
4. **在你满意时请 Claude 提交**。

像人类一样，Claude 的输出往往通过迭代显著改进。虽然第一版可能已经不错，经过 2–3 次迭代后通常会看起来好得多。给 Claude 看到其输出的工具，以获得最佳结果。

### d. 安全的 YOLO 模式

与其监督 Claude，你可以使用 `claude --dangerously-skip-permissions` 绕过所有权限检查，让 Claude 不被打断地工作直到完成。这对修复 lint 错误或生成样板代码等工作流效果很好。

让 Claude 运行任意命令是有风险的，可能导致数据丢失、系统损坏，甚至数据外泄（例如通过 prompt injection 攻击）。为尽量降低这些风险，在没有互联网访问的容器中使用 `--dangerously-skip-permissions`。你可以按照这份使用 Docker Dev Containers 的[参考实现](https://github.com/anthropics/claude-code/tree/main/.devcontainer)操作。

### e. 代码库问答

在上手新代码库时，用 Claude Code 来学习和探索。你可以问 Claude 在结对编程时你会问项目中另一位工程师的同类问题。Claude 可以以智能体方式搜索代码库，回答如下一般问题：

- 日志是如何工作的？
- 我如何创建一个新的 API 端点？
- `foo.rs` 第 134 行的 `async move { ... }` 做什么？
- `CustomerOnboardingFlowImpl` 处理哪些边界情况？
- 为什么我们在第 333 行调用 `foo()` 而不是 `bar()`？
- `baz.py` 第 334 行在 Java 中的等价物是什么？

在 Anthropic，以这种方式使用 Claude Code 已成为我们的核心入职工作流，显著缩短了上手时间，并减少了对其他工程师的负担。不需要特殊 prompting！只需提问，Claude 就会探索代码以找到答案。

### f. 用 Claude 与 git 交互

Claude 可以有效处理许多 git 操作。许多 Anthropic 工程师将 90% 以上的 *git* 交互交给 Claude：

- **搜索 *git* 历史**以回答诸如“哪些改动进入了 v1.2.3？”、“谁拥有这一特定功能？”或“为什么这个 API 被设计成这样？”之类的问题。明确提示 Claude 查阅 git 历史来回答这类查询会有帮助。
- **撰写 commit messages**。Claude 会自动查看你的改动和近期历史，综合考虑所有相关 context 来撰写消息
- **处理复杂的 git 操作**，例如还原文件、解决 rebase 冲突，以及比较和嫁接补丁

### g. 用 Claude 与 GitHub 交互

Claude Code 可以管理许多 GitHub 交互：

- **创建 pull requests**：Claude 理解简写 “pr”，并将基于 diff 和周围 context 生成适当的 commit messages。
- **为一键解决简单的代码审阅评论**：只需告诉它修复你 PR 上的评论（可选地给它更具体的指令），并在完成后推回到 PR 分支。
- **修复失败的构建**或 linter 警告
- **通过请 Claude 遍历开放的 GitHub issues 来分类和分诊开放 issues**

这消除了记住 `gh` 命令行语法的需要，同时自动化日常任务。

### h. 用 Claude 处理 Jupyter notebooks

Anthropic 的研究人员和数据科学家使用 Claude Code 来读写 Jupyter notebooks。Claude 可以解释输出，包括图像，为探索和交互数据提供了一种快速方式。没有必须的 prompts 或工作流，但我们推荐的一种工作流是在 VS Code 中并排打开 Claude Code 和一个 `.ipynb` 文件。

你也可以在把 Jupyter notebook 展示给同事之前，请 Claude 清理或对其做审美改进。明确告诉它让 notebook 或其数据可视化“美观”，往往有助于提醒它正在为人类观看体验做优化。

## 4. 优化你的工作流

下面的建议适用于所有工作流：

### a. 在指令中保持具体

Claude Code 的成功率会随着更具体的指令显著提高，尤其是在第一次尝试时。事先给出清晰方向，可以减少稍后纠正航向的需要。

例如：

| 较差 | 较好 |
| --- | --- |
| add tests for foo.py | write a new test case for foo.py, covering the edge case where the user is logged out. avoid mocks |
| why does ExecutionFactory have such a weird api? | look through ExecutionFactory's git history and summarize how its api came to be |
| add a calendar widget | look at how existing widgets are implemented on the home page to understand the patterns and specifically how code and interfaces are separated out. HotDogWidget.php is a good example to start with. then, follow the pattern to implement a new calendar widget that lets the user select a month and paginate forwards/backwards to pick a year. Build from scratch without libraries other than the ones already used in the rest of the codebase. |

Claude 可以推断意图，但无法读心。具体性会带来与期望更好的对齐。

### b. 给 Claude 图像

Claude 通过几种方法在图像和图表方面表现出色：

- **粘贴截图**（专业提示：在 macOS 中按 *cmd+ctrl+shift+4* 把截图放到剪贴板，再用 *ctrl+v* 粘贴。注意这不是你在 Mac 上通常用来粘贴的 cmd+v，并且不能远程工作。）
- 直接把图像**拖放到** prompt 输入中
- 为图像**提供文件路径**

这在以设计稿作为 UI 开发参考点、以及用视觉图表进行分析和调试时特别有用。即使你没有把视觉内容加入 context，向 Claude 明确说明结果在视觉上吸引人有多重要，仍然会有帮助。

### c. 提及你希望 Claude 查看或处理的文件

使用 tab 补全快速引用仓库中任何位置的文件或文件夹，帮助 Claude 找到或更新正确的资源。

### d. 给 Claude URLs

把特定 URLs 与你的 prompts 一起粘贴，让 Claude 抓取并阅读。为避免对同一域名（例如 docs.foo.com）反复出现权限提示，使用 `/permissions` 把域名加入允许列表。

### e. 尽早、经常地纠正航向

虽然自动接受模式（用 shift+tab 切换）让 Claude 可以自主工作，但作为积极的协作者并引导 Claude 的方法，通常会得到更好结果。你可以通过在开始时向 Claude 彻底解释任务来获得最佳结果，但也可以随时纠正 Claude 的航向。

这四种工具有助于纠正航向：

- **在编码之前请 Claude 制定计划**。明确告诉它在你确认其计划看起来不错之前不要编码。
- **按 Escape 在任何阶段（思考、工具调用、文件编辑）中断 Claude**，保留 context，以便你重定向或扩展指令。
- **双击 Escape 跳回历史**，编辑先前的 prompt，并探索不同方向。你可以编辑 prompt 并重复，直到得到你要找的结果。
- **请 Claude 撤销改动**，常常与选项 #2 结合，以采取不同方法。

尽管 Claude Code 偶尔会在第一次尝试就完美解决问题，使用这些纠正工具通常能更快产生更好的方案。

### f. 使用 `/clear` 保持 context 聚焦

在长时间 sessions 中，Claude 的 context window 可能被无关对话、文件内容和命令填满。这会降低表现，有时还会让 Claude 分心。在任务之间频繁使用 `/clear` 命令来重置 context window。

### g. 对复杂工作流使用检查清单和草稿本

对于有多个步骤或需要穷尽方案的大型任务——例如代码迁移、修复大量 lint 错误，或运行复杂构建脚本——通过让 Claude 使用 Markdown 文件（甚至 GitHub issue！）作为检查清单和工作草稿本，可以提高表现：

例如，要修复大量 lint 问题，你可以这样做：

1. **告诉 Claude 运行 lint 命令**，并把全部结果错误（带文件名和行号）写入一份 Markdown 检查清单
2. **指示 Claude 逐一处理每个问题**，在勾选并进入下一个之前先修复并验证

### h. 把数据传入 Claude

向 Claude 提供数据有几种方法：

- 直接**复制粘贴**进你的 prompt（最常见的方法）
- **管道传入 Claude Code**（例如 `cat foo.txt | claude`），对日志、CSV 和大型数据特别有用
- **告诉 Claude 通过 bash 命令、MCP 工具或定制 slash commands 拉取数据**
- **请 Claude 阅读文件或抓取 URLs**（对图像也有效）

大多数 sessions 会组合使用这些方法。例如，你可以管道传入一个日志文件，然后告诉 Claude 使用某个工具拉取额外 context 来调试日志。

## 5. 使用无头模式自动化你的基础设施

Claude Code 包含[无头模式](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview#automate-ci-and-infra-workflows)，用于 CI、pre-commit hooks、构建脚本和自动化等非交互情境。使用带 prompt 的 `-p` 标志启用无头模式，并用 `--output-format stream-json` 获得流式 JSON 输出。

注意，无头模式不会在 sessions 之间持久化。你必须在每个 session 中触发它。

### a. 用 Claude 做 issue 分诊

无头模式可以为由 GitHub 事件触发的自动化提供动力，例如当仓库中创建了新 issue 时。例如，公开的 [Claude Code 仓库](https://github.com/anthropics/claude-code/blob/main/.github/actions/claude-issue-triage-action/action.yml) 使用 Claude 在新 issues 进入时检查它们并分配适当标签。

### b. 把 Claude 用作 linter

Claude Code 可以提供超出传统 linting 工具所能检测的[主观代码审阅](https://github.com/anthropics/claude-code-action/blob/main/action.yml)，识别拼写错误、过时评论、误导性的函数或变量名等问题。

## 6. 用多 Claude 工作流提升层次

除了单独使用之外，一些最强大的应用涉及并行运行多个 Claude 实例：

### a. 让一个 Claude 写代码；用另一个 Claude 验证

一种简单但有效的方法是让一个 Claude 写代码，而另一个审阅或测试它。类似于与多位工程师共事，有时拥有独立的 context 是有益的：

1. 用 Claude 写代码
2. 运行 `/clear`，或在另一个终端中启动第二个 Claude
3. 让第二个 Claude 审阅第一个 Claude 的工作
4. 再启动一个 Claude（或再次 `/clear`）来阅读代码和审阅反馈
5. 让这个 Claude 根据反馈编辑代码

你也可以对测试做类似的事情：让一个 Claude 写测试，再让另一个 Claude 写代码使测试通过。你甚至可以通过给 Claude 实例各自的工作草稿本、并告诉它们向哪个写、从哪个读，让它们相互通信。

这种分离往往比让单个 Claude 处理一切产生更好的结果。

### b. 拥有仓库的多个 checkouts

与其等待 Claude 完成每一步，许多 Anthropic 工程师会这样做：

1. 在独立文件夹中**创建 3–4 个 git checkouts**
2. 在独立终端标签中**打开每个文件夹**
3. 在每个文件夹中**用不同任务启动 Claude**
4. **轮流检查进度**并批准/拒绝权限请求

### c. 使用 git worktrees

这种方法在多个独立任务上表现出色，提供了比多个 checkouts 更轻量的替代方案。Git worktrees 允许你把同一仓库的多个分支检出到独立目录中。每个 worktree 都有自己的、文件隔离的工作目录，同时共享相同的 Git 历史和 reflog。

使用 git worktrees 使你可以在项目的不同部分同时运行多个 Claude sessions，每个聚焦于自己的独立任务。例如，你可能让一个 Claude 重构认证系统，而另一个构建完全无关的数据可视化组件。因为任务不重叠，每个 Claude 都可以全速工作，而不必等待对方的改动或处理合并冲突：

1. **创建 worktrees**：`git worktree add ../project-feature-a feature-a`
2. **在每个 worktree 中启动 Claude**：`cd ../project-feature-a && claude`
3. 根据需要**创建额外的 worktrees**（在新的终端标签中重复步骤 1–2）

一些提示：

- 使用一致的命名约定
- 为每个 worktree 维护一个终端标签
- 如果你在 Mac 上使用 iTerm2，[设置通知](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview#notification-setup)，以便在 Claude 需要注意时收到提醒
- 为不同 worktrees 使用独立的 IDE 窗口
- 完成后清理：`git worktree remove ../project-feature-a`

### d. 把无头模式与定制 harness 一起使用

`claude -p`（无头模式）以程序方式把 Claude Code 整合进更大的工作流，同时利用其内置工具和 system prompt。使用无头模式有两种主要模式：

1. **扇出（Fanning out）** 处理大型迁移或分析（例如分析数百份日志中的情绪，或分析数千份 CSV）：

   1. 让 Claude 编写一个生成任务列表的脚本。例如，生成一份需要从框架 A 迁移到框架 B 的 2k 个文件的列表。
   2. 遍历任务，以程序方式为每个任务调用 Claude，并给它一项任务和一组可以使用的工具。例如：`claude -p “migrate foo.py from React to Vue. When you are done, you MUST return the string OK if you succeeded, or FAIL if the task failed.” --allowedTools Edit Bash(git commit:*)`
   3. 多次运行该脚本，并精炼你的 prompt 以获得期望结果。

2. **流水线（Pipelining）** 把 Claude 整合进现有的数据/处理流水线：

   1. 调用 `claude -p “<your prompt>” --json | your_command`，其中 `your_command` 是处理流水线的下一步
   2. 就这样！JSON 输出（可选）可以帮助提供结构，以便更容易自动化处理。

对于这两种用例，使用 `--verbose` 标志来调试 Claude 调用会有帮助。我们一般建议在生产中关闭 verbose 模式，以获得更干净的输出。

你在与 Claude Code 共事时有哪些技巧和最佳实践？标记 @AnthropicAI，让我们看看你在构建什么！

## 作者与致谢

由 Boris Cherny 撰写。这项工作汲取了更广泛的 Claude Code 用户社区的最佳实践，他们富有创造性的方法和工作流持续启发着我们。也特别感谢 Daisy Hollman、Ashwin Bhat、Cat Wu、Sid Bidasaria、Cal Rueb、N.T.A.、Barry Zhang、Drew Hodun 以及许多其他 Anthropic 工程师，他们关于 Claude Code 的宝贵洞见和实践经验帮助塑造了这些建议。
