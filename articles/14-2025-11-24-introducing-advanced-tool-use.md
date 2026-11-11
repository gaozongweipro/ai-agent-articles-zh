# 在 Claude Developer Platform 上推出高级工具使用

- 英文标题：Introducing advanced tool use on the Claude Developer Platform
- 中文标题：在 Claude Developer Platform 上推出高级工具使用
- 发布日期：2025-11-24
- 原文链接：https://www.anthropic.com/research/advanced-tool-use
- 翻译类型：全文翻译

---

AI 智能体的未来，是模型能在数百或数千个工具之间无缝工作。一个集成 git 操作、文件操作、包管理器、测试框架和部署流水线的 IDE 助手。一个同时连接 Slack、GitHub、Google Drive、Jira、公司数据库和数十个 MCP servers 的运营协调器。

要[构建有效智能体](https://www.anthropic.com/research/building-effective-agents)，它们需要能使用无限的工具库，而不必事先把每一个定义都塞进 context。我们关于[结合 MCP 进行代码执行](https://www.anthropic.com/engineering/code-execution-with-mcp)的博文讨论过：工具结果和定义有时会在智能体阅读请求之前就消耗 50,000+ tokens。智能体应当按需发现并加载工具，只保留与当前任务相关的部分。

智能体还需要能从代码中调用工具。在使用自然语言工具调用时，每一次调用都需要一次完整的推理过程，中间结果无论是否有用都会堆积在 context 中。代码天然适合编排逻辑，例如循环、条件判断和数据转换。智能体需要根据手头任务，在代码执行和推理之间灵活选择。

智能体还需要从示例中学习正确的工具用法，而不仅仅是 schema 定义。JSON schemas 定义了结构上什么是有效的，但无法表达使用模式：何时包含可选参数、哪些组合有意义，或你的 API 期望怎样的约定。

今天，我们发布三项使这一切成为可能的功能：

- **Tool Search Tool**，使 Claude 能够使用搜索工具访问数千个工具，而不消耗其 context window
- **Programmatic Tool Calling**，使 Claude 能在代码执行环境中调用工具，从而减少对模型 context window 的影响
- **Tool Use Examples**，为演示如何有效使用给定工具提供一套通用标准

在内部测试中，我们发现这些功能帮助我们构建了用传统工具使用模式不可能实现的东西。例如，**[Claude for Excel](https://www.claude.com/claude-for-excel)** 使用 Programmatic Tool Calling 来读取和修改有数千行的电子表格，而不会使模型的 context window 过载。

基于我们的经验，我们相信这些功能为你能用 Claude 构建的东西打开了新可能。

## Tool Search Tool

### 挑战

MCP 工具定义为重要的 context，但随着连接的 servers 增多，这些 tokens 会累积起来。考虑一个五 server 的设置：

- GitHub：35 个工具（约 26K tokens）
- Slack：11 个工具（约 21K tokens）
- Sentry：5 个工具（约 3K tokens）
- Grafana：5 个工具（约 3K tokens）
- Splunk：2 个工具（约 2K tokens）

这是 58 个工具，在对话开始之前就消耗大约 55K tokens。再加入更多 servers，例如 Jira（单独就使用约 17K tokens），你会很快接近 100K+ 的 token 开销。在 Anthropic，我们见过工具定义在优化前消耗 134K tokens。

但 token 成本不是唯一问题。最常见的失败是选错工具和参数不正确，尤其是当工具有相似名称时，例如 `notification-send-user` 与 `notification-send-channel`。

### 我们的方案

与其预先加载全部工具定义，Tool Search Tool 按需发现工具。Claude 只看到当前任务实际需要的工具。

（原文配图：Tool Search Tool 示意图。）

相比 Claude 的传统方法保留 122,800 tokens，Tool Search Tool 保留了 191,300 tokens 的 context。

传统方法：

- 预先加载全部工具定义（50+ 个 MCP 工具约 72K tokens）
- 对话历史和 system prompt 争夺剩余空间
- 总 context 消耗：在任何工作开始之前约 77K tokens

使用 Tool Search Tool：

- 预先只加载 Tool Search Tool（约 500 tokens）
- 按需发现工具（3–5 个相关工具，约 3K tokens）
- 总 context 消耗：约 8.7K tokens，保留 95% 的 context window

这代表 token 用量减少 85%，同时仍能访问完整工具库。内部测试显示，在处理大型工具库时，MCP 评估上的准确率有显著提升。启用 Tool Search Tool 后，Opus 4 从 49% 提升到 74%，Opus 4.5 从 79.5% 提升到 88.1%。

### Tool Search Tool 如何工作

Tool Search Tool 让 Claude 动态发现工具，而不是预先加载全部定义。你向 API 提供全部工具定义，但用 `defer_loading: true` 标记工具，使它们可按需被发现。被延迟加载的工具最初不会被加载进 Claude 的 context。Claude 一开始只看到 Tool Search Tool 本身，以及任何 `defer_loading: false` 的工具（你最关键、最常用的工具）。

当 Claude 需要特定能力时，它会搜索相关工具。Tool Search Tool 返回匹配工具的引用，这些引用会被展开为完整定义并进入 Claude 的 context。

例如，如果 Claude 需要与 GitHub 交互，它会搜索 “github”，然后只有 `github.createPullRequest` 和 `github.listIssues` 被加载——而不是来自 Slack、Jira 和 Google Drive 的其他 50+ 个工具。

这样，Claude 可以访问你的完整工具库，却只为实际需要的工具支付 token 成本。

**关于 prompt caching 的说明：** Tool Search Tool 不会破坏 prompt caching，因为被延迟加载的工具完全被排除在初始 prompt 之外。它们只在 Claude 搜索它们之后才被加入 context，因此你的 system prompt 和核心工具定义仍然可被缓存。

**实现：**

```plaintext
{
  "tools": [
    // Include a tool search tool (regex, BM25, or custom)
    {"type": "tool_search_tool_regex_20251119", "name": "tool_search_tool_regex"},

    // Mark tools for on-demand discovery
    {
      "name": "github.createPullRequest",
      "description": "Create a pull request",
      "input_schema": {...},
      "defer_loading": true
    }
    // ... hundreds more deferred tools with defer_loading: true
  ]
}
```

对于 MCP servers，你可以延迟加载整个 server，同时保持特定高使用率工具被加载：

```plaintext
{
  "type": "mcp_toolset",
  "mcp_server_name": "google-drive",
  "default_config": {"defer_loading": true}, # defer loading the entire server
  "configs": {
    "search_files": {
"defer_loading": false
    }  // Keep most used tool loaded
  }
}
```

Claude Developer Platform 开箱即提供基于 regex 和基于 BM25 的搜索工具，但你也可以使用 embeddings 或其他策略实现定制搜索工具。

### 何时使用 Tool Search Tool

像任何架构决策一样，启用 Tool Search Tool 涉及权衡。该功能在工具调用之前增加一个搜索步骤，因此当 context 节约和准确率提升超过额外延迟时，它能带来最好的投资回报。

**在以下情况使用：**

- 工具定义消耗 >10K tokens
- 遇到工具选择准确率问题
- 构建由多个 servers 驱动的 MCP 系统
- 有 10+ 个可用工具

**在以下情况收益较小：**

- 小型工具库（<10 个工具）
- 每个 session 都频繁使用全部工具
- 工具定义很紧凑

## Programmatic Tool Calling

### 挑战

随着工作流变得更复杂，传统工具调用会造成两个根本问题：

- **中间结果造成的 context 污染**：当 Claude 分析一个 10MB 的日志文件以寻找错误模式时，整个文件会进入其 context window，尽管 Claude 只需要错误频率的摘要。当跨多个表获取客户数据时，每条记录无论是否相关都会在 context 中累积。这些中间结果消耗大量 token 预算，并可能把重要信息完全挤出 context window。
- **推理开销与手工综合**：每一次工具调用都需要一次完整的模型推理过程。在收到结果后，Claude 必须“目测”数据以提取相关信息，推理各部分如何组合，并决定下一步做什么——全部通过自然语言处理完成。一个五工具工作流意味着五次推理过程，外加 Claude 解析每个结果、比较数值并综合结论。这既慢又容易出错。

### 我们的方案

Programmatic Tool Calling 使 Claude 能通过代码而不是一次次单独的 API 往返来编排工具。与其让 Claude 一次请求一个工具、并把每个结果返回到其 context，Claude 会编写调用多个工具、处理其输出、并控制哪些信息真正进入其 context window 的代码。

Claude 擅长写代码；通过让它用 Python 而不是自然语言工具调用来表达编排逻辑，你会得到更可靠、更精确的控制流。循环、条件判断、数据转换和错误处理都在代码中显式表达，而不是隐含在 Claude 的推理中。

#### 示例：预算合规检查

考虑一项常见的业务任务：“哪些团队成员超出了他们的 Q3 差旅预算？”

你有三个可用工具：

- `get_team_members(department)` - 返回带 ID 和级别的团队成员列表
- `get_expenses(user_id, quarter)` - 返回某用户的费用明细项
- `get_budget_by_level(level)` - 返回某一员工级别的预算限额

**传统方法**：

- 获取团队成员 → 20 人
- 对每个人获取其 Q3 费用 → 20 次工具调用，每次返回 50–100 条明细（机票、酒店、餐食、收据）
- 按员工级别获取预算限额
- 所有这些都进入 Claude 的 context：2,000+ 条费用明细（50 KB+）
- Claude 手动加总每个人的费用，查找其预算，并将费用与预算限额比较
- 更多与模型的往返，显著的 context 消耗

**使用 Programmatic Tool Calling**：

与其让每个工具结果返回给 Claude，Claude 会编写一段编排整个工作流的 Python 脚本。该脚本在 Code Execution 工具（一个沙箱环境）中运行，在需要来自你的工具的结果时暂停。当你通过 API 返回工具结果时，它们由脚本处理，而不是被模型消费。脚本继续执行，Claude 只看到最终输出。

（原文配图：Programmatic Tool Calling 流程。）

Programmatic Tool Calling 使 Claude 能通过代码而不是一次次单独的 API 往返来编排工具，从而实现并行工具执行。

下面是 Claude 为预算合规任务编写的编排代码：

```plaintext
team = await get_team_members("engineering")

# Fetch budgets for each unique level
levels = list(set(m["level"] for m in team))
budget_results = await asyncio.gather(*[
    get_budget_by_level(level) for level in levels
])

# Create a lookup dictionary: {"junior": budget1, "senior": budget2, ...}
budgets = {level: budget for level, budget in zip(levels, budget_results)}

# Fetch all expenses in parallel
expenses = await asyncio.gather(*[
    get_expenses(m["id"], "Q3") for m in team
])

# Find employees who exceeded their travel budget
exceeded = []
for member, exp in zip(team, expenses):
    budget = budgets[member["level"]]
    total = sum(e["amount"] for e in exp)
    if total > budget["travel_limit"]:
        exceeded.append({
            "name": member["name"],
            "spent": total,
            "limit": budget["travel_limit"]
        })

print(json.dumps(exceeded))
```

Claude 的 context 只收到最终结果：超出预算的两三个人。那 2,000+ 条明细、中间加总和预算查找都不会影响 Claude 的 context，把消耗从 200KB 的原始费用数据降到仅 1KB 的结果。

效率收益是可观的：

- **Token 节约**：通过把中间结果留在 Claude 的 context 之外，PTC 显著减少 token 消耗。平均用量从 43,588 降到 27,297 tokens，在复杂研究任务上减少 37%。
- **降低延迟**：每一次 API 往返都需要模型推理（数百毫秒到数秒）。当 Claude 在单个代码块中编排 20+ 次工具调用时，你消除了 19+ 次推理过程。API 在不每次返回模型的情况下处理工具执行。
- **提高准确率**：通过编写显式的编排逻辑，Claude 比在自然语言中同时处理多个工具结果时犯更少错误。内部知识检索从 25.6% 提升到 28.5%；[GIA 基准](https://arxiv.org/abs/2311.12983) 从 46.5% 提升到 51.2%。

生产工作流涉及凌乱的数据、条件逻辑，以及需要扩展的操作。Programmatic Tool Calling 让 Claude 以程序方式处理这种复杂度，同时把它的注意力保持在可执行的结果上，而不是原始数据处理上。

### Programmatic Tool Calling 如何工作

#### 1. 将工具标记为可从代码调用

把 code_execution 加入工具，并设置 allowed_callers 以使工具选择加入程序性执行：

```plaintext
{
  "tools": [
    {
      "type": "code_execution_20250825",
      "name": "code_execution"
    },
    {
      "name": "get_team_members",
      "description": "Get all members of a department...",
      "input_schema": {...},
      "allowed_callers": ["code_execution_20250825"] # opt-in to programmatic tool calling
    },
    {
      "name": "get_expenses",
 	...
    },
    {
      "name": "get_budget_by_level",
	...
    }
  ]
}
```

API 会把这些工具定义转换成 Claude 可以调用的 Python 函数。

#### 2. Claude 编写编排代码

与其一次请求一个工具，Claude 会生成 Python 代码：

```plaintext
{
  "type": "server_tool_use",
  "id": "srvtoolu_abc",
  "name": "code_execution",
  "input": {
    "code": "team = get_team_members('engineering')\n..." # the code example above
  }
}
```

#### 3. 工具执行而不进入 Claude 的 context

当代码调用 get_expenses() 时，你会收到带有 caller 字段的工具请求：

```plaintext
{
  "type": "tool_use",
  "id": "toolu_xyz",
  "name": "get_expenses",
  "input": {"user_id": "emp_123", "quarter": "Q3"},
  "caller": {
    "type": "code_execution_20250825",
    "tool_id": "srvtoolu_abc"
  }
}
```

你提供结果，该结果在 Code Execution 环境中被处理，而不是进入 Claude 的 context。这一请求-响应循环会对代码中的每一次工具调用重复进行。

#### 4. 只有最终输出进入 context

当代码运行结束后，只有代码的结果被返回给 Claude：

```plaintext
{
  "type": "code_execution_tool_result",
  "tool_use_id": "srvtoolu_abc",
  "content": {
    "stdout": "[{\"name\": \"Alice\", \"spent\": 12500, \"limit\": 10000}...]"
  }
}
```

这就是 Claude 所看到的全部，而不是沿途处理的 2000+ 条费用明细。

### 何时使用 Programmatic Tool Calling

Programmatic Tool Calling 会在工作流中增加一个代码执行步骤。当 token 节约、延迟改善和准确率提升可观时，这笔额外开销是值得的。

**在以下情况最有益：**

- 处理大型数据集，而你只需要聚合或摘要
- 运行有三个或更多依赖工具调用的多步骤工作流
- 在 Claude 看到工具结果之前先过滤、排序或转换它们
- 处理中间数据不应影响 Claude 推理的任务
- 跨许多项目并行运行操作（例如检查 50 个端点）

**在以下情况收益较小：**

- 进行简单的单工具调用
- 处理 Claude 应当看到并对所有中间结果进行推理的任务
- 运行响应很小的快速查找

## Tool Use Examples

### 挑战

JSON Schema 擅长定义结构——类型、必填字段、允许的枚举——但它无法表达使用模式：何时包含可选参数、哪些组合有意义，或你的 API 期望怎样的约定。

考虑一个支持工单 API：

```plaintext
{
  "name": "create_ticket",
  "input_schema": {
    "properties": {
      "title": {"type": "string"},
      "priority": {"enum": ["low", "medium", "high", "critical"]},
      "labels": {"type": "array", "items": {"type": "string"}},
      "reporter": {
        "type": "object",
        "properties": {
          "id": {"type": "string"},
          "name": {"type": "string"},
          "contact": {
            "type": "object",
            "properties": {
              "email": {"type": "string"},
              "phone": {"type": "string"}
            }
          }
        }
      },
      "due_date": {"type": "string"},
      "escalation": {
        "type": "object",
        "properties": {
          "level": {"type": "integer"},
          "notify_manager": {"type": "boolean"},
          "sla_hours": {"type": "integer"}
        }
      }
    },
    "required": ["title"]
  }
}
```

Schema 定义了什么是有效的，但留下了关键问题未答：

- **格式歧义：** `due_date` 应当使用 “2024-11-06”、“Nov 6, 2024”，还是 “2024-11-06T00:00:00Z”？
- **ID 约定：** `reporter.id` 是 UUID、“USR-12345”，还是仅仅 “12345”？
- **嵌套结构用法：** Claude 何时应当填充 `reporter.contact`？
- **参数相关性：** `escalation.level` 和 `escalation.sla_hours` 与优先级如何关联？

这些歧义可能导致格式错误的工具调用和不一致的参数使用。

### 我们的方案

Tool Use Examples 让你直接在工具定义中提供示例工具调用。与其仅依赖 schema，你向 Claude 展示具体的使用模式：

```plaintext
{
    "name": "create_ticket",
    "input_schema": { /* same schema as above */ },
    "input_examples": [
      {
        "title": "Login page returns 500 error",
        "priority": "critical",
        "labels": ["bug", "authentication", "production"],
        "reporter": {
          "id": "USR-12345",
          "name": "Jane Smith",
          "contact": {
            "email": "jane@acme.com",
            "phone": "+1-555-0123"
          }
        },
        "due_date": "2024-11-06",
        "escalation": {
          "level": 2,
          "notify_manager": true,
          "sla_hours": 4
        }
      },
      {
        "title": "Add dark mode support",
        "labels": ["feature-request", "ui"],
        "reporter": {
          "id": "USR-67890",
          "name": "Alex Chen"
        }
      },
      {
        "title": "Update API documentation"
      }
    ]
  }
```

从这三个示例中，Claude 学到：

- **格式约定**：日期使用 YYYY-MM-DD，用户 ID 遵循 USR-XXXXX，标签使用 kebab-case
- **嵌套结构模式**：如何构造带有嵌套 contact 对象的 reporter 对象
- **可选参数相关性**：严重 bug 有完整联系信息 + 带有紧 SLA 的升级；功能请求有 reporter 但没有 contact/escalation；内部任务只有标题

在我们自己的内部测试中，工具使用示例把复杂参数处理的准确率从 72% 提升到 90%。

### 何时使用 Tool Use Examples

Tool Use Examples 会为工具定义增加 tokens，因此当准确率提升超过额外成本时，它们最有价值。

**在以下情况最有益：**

- 复杂嵌套结构，有效 JSON 并不意味着正确用法
- 有许多可选参数、且包含模式很重要的工具
- 带有 schema 未能捕捉的领域特定约定的 API
- 相似工具，示例可以澄清该用哪一个（例如 `create_ticket` vs `create_incident`）

**在以下情况收益较小：**

- 用法显而易见的简单单参数工具
- Claude 已经理解的标准格式，例如 URL 或电子邮件
- 由 JSON Schema 约束更好地处理的验证问题

## 最佳实践

构建会采取现实世界行动的智能体，意味着同时处理规模、复杂度和精度。这三项功能协同工作，解决工具使用工作流中的不同瓶颈。下面是如何有效组合它们。

### 有策略地分层使用功能

并非每个智能体在给定任务上都需要使用全部三项功能。从你最大的瓶颈开始：

- 工具定义造成的 context 膨胀 → Tool Search Tool
- 大型中间结果污染 context → Programmatic Tool Calling
- 参数错误和格式错误的调用 → Tool Use Examples

这种聚焦方法让你能解决限制智能体表现的具体约束，而不是预先增加复杂度。

然后根据需要叠加额外功能。它们是互补的：Tool Search Tool 确保找到正确的工具，Programmatic Tool Calling 确保高效执行，Tool Use Examples 确保正确调用。

### 设置 Tool Search Tool 以获得更好的发现

工具搜索会匹配名称和描述，因此清晰、描述性的定义能提高发现准确率。

```plaintext
// Good
{
    "name": "search_customer_orders",
    "description": "Search for customer orders by date range, status, or total amount. Returns order details including items, shipping, and payment info."
}

// Bad
{
    "name": "query_db_orders",
    "description": "Execute order query"
}
```

加入 system prompt 指导，使 Claude 知道有哪些可用能力：

```plaintext
You have access to tools for Slack messaging, Google Drive file management, 
Jira ticket tracking, and GitHub repository operations. Use the tool search 
to find specific capabilities.
```

始终加载你最常用的三到五个工具，其余延迟加载。这在常见操作的即时访问与其他一切的按需发现之间取得平衡。

### 设置 Programmatic Tool Calling 以获得正确执行

因为 Claude 会编写代码来解析工具输出，请清晰记录返回格式。这有助于 Claude 编写正确的解析逻辑：

```plaintext
{
    "name": "get_orders",
    "description": "Retrieve orders for a customer.
Returns:
    List of order objects, each containing:
    - id (str): Order identifier
    - total (float): Order total in USD
    - status (str): One of 'pending', 'shipped', 'delivered'
    - items (list): Array of {sku, quantity, price}
    - created_at (str): ISO 8601 timestamp"
}
```

以下是适合从程序性编排中获益、应当选择加入的工具：

- 可以并行运行的工具（独立操作）
- 可以安全重试的操作（幂等）

### 设置 Tool Use Examples 以提高参数准确率

为行为清晰度精心制作示例：

- 使用真实数据（真实城市名、合理价格，而不是 “string” 或 “value”）
- 用最小、部分和完整规格模式展示多样性
- 保持简洁：每个工具 1–5 个示例
- 聚焦于歧义（只在正确用法从 schema 中并不显而易见的地方添加示例）

## 如何开始

这些功能以 beta 形式提供。要启用它们，加入 beta header 并包含你需要的工具：

```plaintext
client.beta.messages.create(
    betas=["advanced-tool-use-2025-11-20"],
    model="claude-sonnet-4-5-20250929",
    max_tokens=4096,
    tools=[
        {"type": "tool_search_tool_regex_20251119", "name": "tool_search_tool_regex"},
        {"type": "code_execution_20250825", "name": "code_execution"},
        # Your tools with defer_loading, allowed_callers, and input_examples
    ]
)
```

详细的 API 文档和 SDK 示例见：

- Tool Search Tool 的[文档](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool)和 [cookbook](https://github.com/anthropics/claude-cookbooks/blob/main/tool_use/tool_search_with_embeddings.ipynb)
- Programmatic Tool Calling 的[文档](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling)和 [cookbook](https://github.com/anthropics/claude-cookbooks/blob/main/tool_use/programmatic_tool_calling_ptc.ipynb)
- Tool Use Examples 的[文档](https://platform.claude.com/docs/en/agents-and-tools/tool-use/implement-tool-use#providing-tool-use-examples)

这些功能把工具使用从简单的函数调用推向智能编排。随着智能体处理跨越数十个工具和大型数据集的更复杂工作流，动态发现、高效执行和可靠调用成为基础。

我们期待看到你构建的东西。

## 作者与致谢

由 Bin Wu 撰写，Adam Jones、Artur Renault、Henry Tay、Jake Noble、Noah Picard、Sam Jiang 以及 Claude Developer Platform 团队亦有贡献。这项工作建立在 Chris Gorgolewski、Daniel Jiang、Jeremy Fox 和 Mike Lambert 的基础研究之上。我们也从整个 AI 生态中获得启发，包括 [Joel Pobar 的 LLMVM](https://github.com/9600dev/llmvm)、[Cloudflare 的 Code Mode](https://blog.cloudflare.com/code-mode/) 以及 [Code Execution as MCP](https://www.anthropic.com/engineering/code-execution-with-mcp)。特别感谢 Andy Schumeister、Hamish Kerr、Keir Bradwell、Matt Bleifer 和 Molly Vorwerck 的支持。
