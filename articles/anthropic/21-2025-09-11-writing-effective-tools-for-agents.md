---
title_en: Writing effective tools for agents — with agents
title_zh: 为智能体撰写有效工具——与智能体一起
company: anthropic
date: 2025-09-11
url: https://www.anthropic.com/research/writing-tools-for-agents
type: full
category: 工具与协议
tags:
  - 工具调用
  - 工具设计
  - 构建智能体
---

# 为智能体撰写有效工具——与智能体一起

[Model Context Protocol（MCP）](https://modelcontextprotocol.io/docs/getting-started/intro) 可以赋予 LLM 智能体潜在数百个工具，以解决现实世界任务。但我们如何让这些工具最大限度地有效？

本文将描述我们在各种智能体式 AI 系统中提升表现的最有效技术。[^1]

我们首先介绍你可以如何：

- 构建并测试工具原型
- 与智能体一起为你的工具创建并运行全面评估
- 与 Claude Code 等智能体协作，自动提高工具表现

最后，我们总结沿途识别出的撰写高质量工具的关键原则：

- 选择正确的工具去实现（以及不去实现）
- 通过 namespacing 为功能划定清晰边界
- 从工具向智能体返回有意义的 context
- 针对 token 效率优化工具响应
- 对工具描述和规格做 prompt-engineering

（原文配图：工程师如何使用 Claude Code 评估智能体工具有效性。）

构建评估使你可以系统地衡量工具表现。你可以使用 Claude Code 针对该评估自动优化你的工具。

## 什么是工具？

在计算中，确定性系统在给定相同输入时每次都产生相同输出，而*非确定性*系统——例如智能体——即使起始条件相同，也可能生成不同的响应。

当我们传统地编写软件时，我们是在确定性系统之间建立契约。例如，像 `getWeather("NYC")` 这样的函数调用，每次被调用时都会以完全相同的方式获取纽约市的天气。

工具是一种新的软件，它反映的是确定性系统与非确定性智能体之间的契约。当用户问“我今天该带伞吗？”时，智能体可能调用天气工具、凭一般知识作答，甚至先问一个关于地点的澄清问题。偶尔，智能体可能产生幻觉，甚至未能理解如何使用某个工具。

这意味着在为智能体编写软件时，我们需要从根本上重新思考方法：不要像为其他开发者或系统编写函数和 API 那样编写工具和 [MCP servers](https://modelcontextprotocol.io/)，而需要为智能体来设计它们。

我们的目标是扩大智能体能够有效解决广泛任务的表面区域，使它们能够使用工具追求多种成功策略。幸运的是，根据我们的经验，对智能体最“符合人体工学（ergonomic）”的工具，对人类来说往往也出人意料地直观。

## 如何撰写工具

在这一部分，我们描述你可以如何与智能体协作，既撰写又改进你交给它们的工具。先快速搭建工具原型并在本地测试。接下来，运行全面评估以衡量后续改动。与智能体一起工作，你可以重复评估并改进工具的过程，直到你的智能体在现实世界任务上取得强表现。

### 构建原型

如果自己不亲自动手，很难预先判断哪些工具对智能体会符合人体工学、哪些不会。先快速搭建工具原型。如果你使用 [Claude Code](https://www.anthropic.com/claude-code) 来编写工具（甚至可能一次性完成），给 Claude 提供你的工具将依赖的任何软件库、API 或 SDK（包括可能的 [MCP SDK](https://modelcontextprotocol.io/docs/sdk)）的文档会有帮助。对 LLM 友好的文档通常可以在官方文档站点的扁平 `llms.txt` 文件中找到（这是我们 [API 的](https://docs.anthropic.com/llms.txt)）。

把工具包装在 [本地 MCP server](https://modelcontextprotocol.io/docs/develop/connect-local-servers) 或 [Desktop extension](https://www.anthropic.com/engineering/desktop-extensions)（DXT）中，就可以在 Claude Code 或 Claude Desktop 应用中连接并测试你的工具。

要将本地 MCP server 连接到 Claude Code，运行 `claude mcp add <name> <command> [args...]`。

要将本地 MCP server 或 DXT 连接到 Claude Desktop 应用，分别前往 `Settings > Developer` 或 `Settings > Extensions`。

工具也可以直接传入 [Anthropic API](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/overview) 调用，以便进行程序性测试。

亲自测试工具以识别任何粗糙之处。收集用户反馈，以建立对你期望工具所能支持的用例和 prompts 的直觉。

### 运行评估

接下来，你需要通过运行评估来衡量 Claude 使用你的工具的表现。先基于现实世界用途生成大量评估任务。我们建议与智能体协作，帮助分析你的结果并确定如何改进工具。在我们的 [tool evaluation cookbook](https://platform.claude.com/cookbook/tool-evaluation-tool-evaluation) 中可以端到端地看到这一过程。

（原文配图：人工撰写 vs. Claude 优化的 Slack MCP servers 在测试集上的准确率。）

我们内部 Slack 工具在留出测试集上的表现

#### 生成评估任务

有了早期原型后，Claude Code 可以迅速探索你的工具，并创建数十对 prompt 与响应。Prompts 应受现实世界用途启发，并基于真实的数据源和服务（例如内部知识库和微服务）。我们建议避免过于简单或表面的 “sandbox” 环境，它们无法以足够的复杂度对你的工具做压力测试。强评估任务可能需要多次工具调用——潜在地达到数十次。

以下是一些强任务的例子：

- 下周与 Jane 安排一次会议，讨论我们最新的 Acme Corp 项目。附上我们上次项目规划会议的笔记，并预订一间会议室。
- 客户 ID 9182 报告说一次购买尝试被扣费三次。找出所有相关日志条目，并确定是否有其他客户受到同一问题影响。
- 客户 Sarah Chen 刚刚提交了取消请求。准备一份挽留方案。确定：(1) 他们为什么离开，(2) 什么样的挽留方案最有说服力，以及 (3) 在提出方案前我们应了解的任何风险因素。

以下是一些较弱的任务：

- 下周与 jane@acme.corp 安排一次会议。
- 在支付日志中搜索 `purchase_complete` 和 `customer_id=9182`。
- 查找客户 ID 45892 的取消请求。

每个评估 prompt 都应当配对一个可验证的响应或结果。你的验证器可以简单到对 ground truth 与采样响应做精确字符串比较，也可以先进到让 Claude 来评判响应。避免过于严格的验证器因格式、标点或有效的替代措辞等无关差异而拒绝正确响应。

对于每一对 prompt-响应，你也可以选择指定你期望智能体在解决该任务时调用的工具，以衡量评估期间智能体是否成功把握了每个工具的用途。然而，因为正确解决问题可能有多条有效路径，尽量避免对策略过度指定或过拟合。

#### 运行评估

我们建议通过直接的 LLM API 调用以程序方式运行评估。使用简单的智能体循环（包裹交替进行的 LLM API 与工具调用的 `while` 循环）：每个评估任务一个循环。每个评估智能体应当被给予单个任务 prompt 以及你的工具。

在评估智能体的 system prompts 中，我们建议指示智能体不仅输出结构化的响应块（用于验证），还输出推理和反馈块。指示智能体在工具调用和响应块*之前*输出这些内容，可能通过触发思维链（chain-of-thought，CoT）行为来提高 LLM 的有效智能。

如果你使用 Claude 运行评估，可以开启 [interleaved thinking](https://docs.anthropic.com/en/docs/build-with-claude/extended-thinking#interleaved-thinking) 以获得类似的“开箱即用”功能。这将帮助你探究智能体为何调用或不调用某些工具，并突出工具描述和规格中需要改进的具体方面。

除了顶层准确率之外，我们还建议收集其他指标，例如单个工具调用和任务的总运行时间、工具调用总次数、总 token 消耗，以及工具错误。跟踪工具调用可以帮助揭示智能体追求的常见工作流，并为工具合并提供一些机会。

（原文配图：人工撰写 vs. Claude 优化的 Asana MCP servers 在测试集上的准确率。）

我们内部 Asana 工具在留出测试集上的表现

#### 分析结果

智能体是你发现问题和提供反馈的有用伙伴，反馈范围从相互矛盾的工具描述，到低效的工具实现和令人困惑的工具 schemas。不过请记住，智能体在反馈和响应中*省略*的内容，往往比它们包含的内容更重要。LLM 并不总是[说出它们的本意](https://www.anthropic.com/research/tracing-thoughts-language-model)。

观察智能体在何处卡住或困惑。阅读评估智能体的推理和反馈（或 CoT），以识别粗糙之处。审阅原始 transcripts（包括工具调用和工具响应），以捕捉智能体 CoT 中未明确描述的任何行为。读出字里行间的意思；记住，你的评估智能体并不一定知道正确答案和策略。

分析你的工具调用指标。大量冗余的工具调用可能表明分页或 token 限制参数需要适当调整；大量因无效参数导致的工具错误可能表明工具可以使用更清晰的描述或更好的示例。当我们推出 Claude 的 [web search 工具](https://www.anthropic.com/news/web-search) 时，我们发现 Claude 不必要地在工具的 `query` 参数后附加 `2025`，从而偏向搜索结果并降低表现（我们通过改进工具描述，把 Claude 引导到正确方向）。

### 与智能体协作

你甚至可以让智能体分析你的结果并为你改进工具。只需把评估智能体的 transcripts 拼接起来，粘贴进 Claude Code。Claude 擅长分析 transcripts 并一次性重构大量工具——例如，确保在做出新改动时，工具实现和描述保持自洽。

事实上，本文中的大部分建议，都来自我们反复用 Claude Code 优化内部工具实现的过程。我们的评估建立在内部工作空间之上，镜像了内部工作流的复杂度，包括真实项目、文档和消息。

我们依赖留出测试集来确保不会过拟合到我们的“训练”评估。这些测试集揭示，即使超出我们用“专家”工具实现所达到的水平，我们仍能提取额外的表现改进——无论这些工具是由我们的研究人员手工撰写，还是由 Claude 自己生成。

在下一部分，我们将分享从这一过程中学到的一些内容。

## 撰写有效工具的原则

在这一部分，我们将所学提炼为撰写有效工具的几条指导原则。

### 为智能体选择正确的工具

更多工具并不总是带来更好结果。我们观察到的一个常见错误是：工具仅仅包装现有软件功能或 API 端点——无论这些工具是否适合智能体。这是因为智能体对传统软件有不同的 “affordances（可供性）”——也就是说，它们感知自己可以用这些工具采取哪些潜在行动的方式不同。

LLM 智能体的 “context” 是有限的（也就是说，它们一次能处理的信息量有限），而计算机内存便宜且丰富。考虑在通讯录中搜索联系人的任务。传统软件程序可以高效地逐个存储和处理联系人列表，检查完一个再继续下一个。

然而，如果 LLM 智能体使用一个返回*全部*联系人的工具，然后必须逐 token 阅读每一个，它就是在把有限的 context 空间浪费在无关信息上（想象一下通过从上到下阅读每一页来在通讯录中搜索联系人——也就是暴力搜索）。更好、也更自然的方法（对智能体和人类都是如此）是先跳到相关页面（也许按字母顺序找到它）。

我们建议构建少量深思熟虑的工具，瞄准与评估任务相匹配的特定高影响力工作流，并从此扩展。在通讯录的情形中，你可能选择实现 `search_contacts` 或 `message_contact` 工具，而不是 `list_contacts` 工具。

工具可以合并功能，在底层处理潜在*多个*离散操作（或 API 调用）。例如，工具可以用相关元数据丰富工具响应，或在单次工具调用中处理经常被串联的多步骤任务。

以下是一些例子：

- 与其实现 `list_users`、`list_events` 和 `create_event` 工具，不如考虑实现一个 `schedule_event` 工具，它能查找空闲时间并安排事件。
- 与其实现 `read_logs` 工具，不如考虑实现一个 `search_logs` 工具，它只返回相关日志行及其周围的一些 context。
- 与其实现 `get_customer_by_id`、`list_transactions` 和 `list_notes` 工具，不如实现一个 `get_customer_context` 工具，一次性汇编客户所有最近且相关的信息。

确保你构建的每个工具都有清晰、独特的用途。工具应当使智能体能以与人类在获得相同底层资源时大致相同的方式划分并解决问题，同时减少本会被中间输出消耗的 context。

太多工具或相互重叠的工具，也可能让智能体从追求高效策略中分心。对你构建（或不构建）的工具进行仔细、有选择的规划，真的会有回报。

### 为工具做 Namespacing

你的 AI 智能体将潜在地获得数十个 MCP servers 和数百个不同工具的访问权限——包括其他开发者的工具。当工具在功能上重叠或用途模糊时，智能体可能对使用哪些工具感到困惑。

Namespacing（在共同前缀下对相关工具分组）可以帮助在大量工具之间划定边界；MCP clients 有时默认会这样做。例如，按服务（如 `asana_search`、`jira_search`）和按资源（如 `asana_projects_search`、`asana_users_search`）对工具做 namespacing，可以帮助智能体在正确的时间选择正确的工具。

我们发现，在基于前缀和基于后缀的 namespacing 之间做选择，对我们的工具使用评估有不可忽视的影响。效果因 LLM 而异，我们鼓励你根据自己的评估选择命名方案。

智能体可能调用错误的工具、用错误的参数调用正确的工具、调用过少的工具，或错误地处理工具响应。通过有选择地实现名称反映任务自然划分的工具，你可以同时减少加载进智能体 context 的工具和工具描述数量，并把智能体式计算从智能体的 context 卸载回工具调用本身。这降低了智能体犯错的总体风险。

### 从工具返回有意义的 context

同样地，工具实现应当注意只向智能体返回高信号信息。它们应当优先考虑上下文相关性而非灵活性，并避开低层技术标识符（例如：`uuid`、`256px_image_url`、`mime_type`）。像 `name`、`image_url` 和 `file_type` 这样的字段，更有可能直接告知智能体的下游动作和响应。

智能体在处理自然语言名称、术语或标识符时，也往往比处理隐晦标识符成功得多。我们发现，仅仅把任意字母数字 UUID 解析为语义上更有意义、更可解释的语言（甚至是从 0 开始的 ID 方案），就能通过减少幻觉显著提高 Claude 在检索任务上的精度。

在某些情形中，智能体可能需要灵活地与自然语言和技术标识符输出交互，哪怕只是为了触发下游工具调用（例如，`search_user(name='jane')` → `send_message(id=12345)`）。你可以通过在工具中暴露一个简单的 `response_format` 枚举参数来同时支持两者，让智能体控制工具返回 `“concise”` 还是 `“detailed”` 响应（见原文配图）。

你可以添加更多格式以获得更大灵活性，类似于 GraphQL，你可以精确选择希望接收哪些信息。下面是一个用于控制工具响应详尽程度的 ResponseFormat 枚举示例：

```plaintext
enum ResponseFormat {
   DETAILED = "detailed",
   CONCISE = "concise"
}
```

下面是一份详细工具响应的例子（206 tokens）：

（原文配图：详细工具响应的代码片段。）

下面是一份简洁工具响应的例子（72 tokens）：

（原文配图：简洁工具响应的代码片段。）

Slack 线程和线程回复由唯一的 `thread_ts` 标识，获取线程回复需要用到它们。`thread_ts` 和其他 ID（`channel_id`、`user_id`）可以从 `“detailed”` 工具响应中检索，以便启用需要这些 ID 的进一步工具调用。`“concise”` 工具响应只返回线程内容并排除 ID。在这个例子中，使用 `“concise”` 工具响应只用了大约 ⅓ 的 tokens。

甚至你的工具响应结构——例如 XML、JSON 或 Markdown——也可能对评估表现产生影响：没有放之四海而皆准的方案。这是因为 LLM 是按 next-token prediction 训练的，往往在与训练数据匹配的格式上表现更好。最优响应结构会因任务和智能体而有很大差异。我们鼓励你根据自己的评估选择最佳响应结构。

### 针对 token 效率优化工具响应

优化 context 的*质量*很重要。但优化工具响应中返回给智能体的 context *数量*同样重要。

我们建议对任何可能消耗大量 context 的工具响应，实现分页、范围选择、过滤和/或截断的某种组合，并配以合理的默认参数值。对于 Claude Code，我们默认将工具响应限制为 25,000 tokens。我们预期智能体的有效 context 长度会随时间增长，但对 context 高效的工具的需求仍将存在。

如果选择截断响应，务必用有帮助的指令引导智能体。你可以直接鼓励智能体追求对 token 更高效的策略，例如在知识检索任务中进行许多小而有针对性的搜索，而不是一次宽泛的搜索。类似地，如果工具调用引发错误（例如在输入验证期间），你可以对错误响应做 prompt-engineering，清晰传达具体、可执行的改进，而不是不透明的错误代码或 tracebacks。

下面是一份被截断的工具响应示例：

（原文配图：被截断的工具响应示例。）

下面是一份无帮助的错误响应示例：

（原文配图：无帮助的工具响应示例。）

下面是一份有帮助的错误响应示例：

（原文配图：有帮助的错误响应示例。）

工具截断和错误响应可以引导智能体走向对 token 更高效的工具使用行为（使用过滤器或分页），或给出正确格式化的工具输入示例。

### 对工具描述做 Prompt-engineering

我们现在来到改进工具最有效的方法之一：对工具描述和规格做 prompt-engineering。因为这些会被加载进智能体的 context，它们可以共同把智能体引导向有效的工具调用行为。

在撰写工具描述和规格时，想象你会如何向团队中的一名新员工描述你的工具。考虑你可能隐含带入的 context——专门的查询格式、小众术语的定义、底层资源之间的关系——并把它说清楚。通过清晰描述（并用严格的数据模型强制执行）期望的输入和输出，避免歧义。尤其是，输入参数应当被无歧义地命名：不要用名为 `user` 的参数，试着用名为 `user_id` 的参数。

有了评估，你可以更有信心地衡量 prompt engineering 的影响。即使对工具描述的细小改进也可能带来显著提升。Claude Sonnet 3.5 在我们对工具描述做了精确改进之后，在 [SWE-bench Verified](https://www.anthropic.com/engineering/swe-bench-sonnet) 评估上达到了当时最先进的表现，显著降低了错误率并提高了任务完成度。

其他工具定义最佳实践见我们的 [Developer Guide](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/implement-tool-use#best-practices-for-tool-definitions)。如果你在为 Claude 构建工具，我们还建议阅读工具如何被动态加载进 Claude 的 [system prompt](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/implement-tool-use#tool-use-system-prompt)。最后，如果你在为 MCP server 撰写工具，[tool annotations](https://modelcontextprotocol.io/specification/2025-06-18/server/tools) 可以帮助披露哪些工具需要开放世界访问，或会做出破坏性更改。

## 展望

要为智能体构建有效工具，我们需要把软件开发实践从可预测、确定性的模式，重新定向到非确定性的模式。

通过本文描述的迭代、评估驱动的过程，我们识别出成功工具的一致模式：有效工具被有意识且清晰地定义，谨慎使用智能体 context，可以在多样工作流中组合在一起，并使智能体能直观地解决现实世界任务。

未来，我们预期智能体与世界交互的具体机制会演化——从 MCP 协议的更新，到底层 LLM 本身的升级。凭借系统性的、评估驱动的方法来改进面向智能体的工具，我们可以确保：随着智能体变得更有能力，它们使用的工具也将与之一同演化。

## 作者与致谢

由 Ken Aizawa 撰写，并得到研究（Barry Zhang、Zachary Witten、Daniel Jiang、Sami Al-Sheikh、Matt Bell、Maggie Vo）、MCP（Theodora Chu、John Welsh、David Soria Parra、Adam Jones）、产品工程（Santiago Seira）、市场（Molly Vorwerck）、设计（Drew Roper）和应用 AI（Christian Ryan、Alexander Bricken）同事的宝贵贡献。

## 脚注

[^1]: 除了训练底层 LLM 本身之外。
