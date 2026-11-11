# 结合 MCP 的代码执行：构建更高效的智能体

- 英文标题：Code execution with MCP: Building more efficient agents
- 中文标题：结合 MCP 的代码执行：构建更高效的智能体
- 发布日期：2025-11-04
- 原文链接：https://www.anthropic.com/research/code-execution-with-mcp
- 翻译类型：全文翻译

---

[Model Context Protocol（MCP）](https://modelcontextprotocol.io/) 是将 AI 智能体连接到外部系统的开放标准。传统上，把智能体连接到工具和数据，需要对每一对组合做定制集成，造成碎片化和重复劳动，难以规模化地构建真正互联的系统。MCP 提供了一种通用协议——开发者在智能体中实现一次 MCP，就能解锁整个集成生态。

自 2024 年 11 月发布 MCP 以来，采用速度很快：社区已构建了数千个 [MCP servers](https://github.com/modelcontextprotocol/servers)，[SDK](https://modelcontextprotocol.io/docs/sdk) 覆盖所有主要编程语言，业界也将 MCP 视为连接智能体与工具、数据的事实标准。

如今，开发者经常构建能访问数十个 MCP servers、成百上千个工具的智能体。然而，随着所连接工具数量增长，预先加载全部工具定义、并把中间结果传入 context window，会拖慢智能体并增加成本。

本文将探讨代码执行如何让智能体更高效地与 MCP servers 交互：在使用更少 token 的同时处理更多工具。

## 工具过度消耗 token，使智能体效率下降

随着 MCP 使用规模扩大，有两种常见模式会增加智能体的成本和延迟：

1. 工具定义使 context window 过载；
2. 中间工具结果消耗额外 token。

### 1. 工具定义使 context window 过载

大多数 MCP 客户端会把全部工具定义预先直接加载进 context，用直接的工具调用语法把它们暴露给模型。这些工具定义可能看起来像：

```plaintext
gdrive.getDocument
     Description: Retrieves a document from Google Drive
     Parameters:
                documentId (required, string): The ID of the document to retrieve
                fields (optional, string): Specific fields to return
     Returns: Document object with title, body content, metadata, permissions, etc.
```

```plaintext
salesforce.updateRecord
    Description: Updates a record in Salesforce
    Parameters:
               objectType (required, string): Type of Salesforce object (Lead, Contact,      Account, etc.)
               recordId (required, string): The ID of the record to update
               data (required, object): Fields to update with their new values
     Returns: Updated record object with confirmation
```

工具描述会占用更多 context window 空间，从而增加响应时间和成本。当智能体连接到数千个工具时，它们在阅读请求之前就需要处理数十万 token。

### 2. 中间工具结果消耗额外 token

大多数 MCP 客户端允许模型直接调用 MCP 工具。例如，你可能对智能体说：“把我的会议记录从 Google Drive 下载下来，附加到这个 Salesforce lead 上。”

模型会进行类似这样的调用：

```plaintext
TOOL CALL: gdrive.getDocument(documentId: "abc123")
        → returns "Discussed Q4 goals...\n[full transcript text]"
           (loaded into model context)

TOOL CALL: salesforce.updateRecord(
			objectType: "SalesMeeting",
			recordId: "00Q5f000001abcXYZ",
  			data: { "Notes": "Discussed Q4 goals...\n[full transcript text written out]" }
		)
		(model needs to write entire transcript into context again)
```

每个中间结果都必须经过模型。在这个例子中，完整通话记录流过了两次。对于一场 2 小时的销售会议，这可能意味着额外处理 50,000 个 token。更大的文档甚至可能超出 context window 限制，使工作流中断。

面对大型文档或复杂数据结构时，模型在工具调用之间复制数据也更容易出错。

MCP 客户端把工具定义加载进模型的 context window，并编排一个消息循环：每次工具调用和结果都在操作之间经过模型。

## 结合 MCP 的代码执行提高 context 效率

随着代码执行环境在智能体中越来越常见，一种解决方案是把 MCP servers 呈现为代码 API，而不是直接的工具调用。智能体随后可以编写代码来与 MCP servers 交互。这种方法同时解决了上述两个挑战：智能体可以只加载所需的工具，并在执行环境中处理数据，然后再把结果传回模型。

实现方式有多种。一种做法是根据已连接的 MCP servers 生成所有可用工具的文件树。下面是一个使用 TypeScript 的实现：

```plaintext
servers
├── google-drive
│   ├── getDocument.ts
│   ├── ... (other tools)
│   └── index.ts
├── salesforce
│   ├── updateRecord.ts
│   ├── ... (other tools)
│   └── index.ts
└── ... (other servers)
```

然后每个工具对应一个文件，类似于：

```plaintext
// ./servers/google-drive/getDocument.ts
import { callMCPTool } from "../../../client.js";

interface GetDocumentInput {
  documentId: string;
}

interface GetDocumentResponse {
  content: string;
}

/* Read a document from Google Drive */
export async function getDocument(input: GetDocumentInput): Promise<GetDocumentResponse> {
  return callMCPTool<GetDocumentResponse>('google_drive__get_document', input);
}
```

上面从 Google Drive 到 Salesforce 的例子就变成了这样的代码：

```plaintext
// Read transcript from Google Docs and add to Salesforce prospect
import * as gdrive from './servers/google-drive';
import * as salesforce from './servers/salesforce';

const transcript = (await gdrive.getDocument({ documentId: 'abc123' })).content;
await salesforce.updateRecord({
  objectType: 'SalesMeeting',
  recordId: '00Q5f000001abcXYZ',
  data: { Notes: transcript }
});
```

智能体通过探索文件系统来发现工具：列出 `./servers/` 目录以找到可用的 servers（如 `google-drive` 和 `salesforce`），然后读取它需要的具体工具文件（如 `getDocument.ts` 和 `updateRecord.ts`）以理解每个工具的接口。这让智能体只需为当前任务加载所需的定义。这将 token 用量从 150,000 降到 2,000——时间和成本节约达 98.7%。

Cloudflare 发表了[类似发现](https://blog.cloudflare.com/code-mode/)，把结合 MCP 的代码执行称为 “Code Mode”。核心洞见是相同的：LLM 擅长写代码，开发者应利用这一优势，构建能更高效与 MCP servers 交互的智能体。

## 结合 MCP 进行代码执行的好处

结合 MCP 的代码执行，通过按需加载工具、在数据到达模型之前先行过滤，以及在单步中执行复杂逻辑，使智能体能更高效地使用 context。这一方法还有安全和状态管理方面的好处。

### Progressive disclosure（渐进式披露）

模型非常擅长浏览文件系统。把工具以代码形式放在文件系统上，可以让模型按需读取工具定义，而不是一次性全部读入。

或者，也可以在 server 上增加一个 `search_tools` 工具来查找相关定义。例如，在使用上文假设的 Salesforce server 时，智能体搜索 “salesforce”，并只加载当前任务所需的那些工具。在 `search_tools` 中加入一个 detail level 参数，让智能体选择所需的详细程度（例如仅名称、名称加描述、或带 schemas 的完整定义），也有助于智能体节约 context 并高效找到工具。

### 对 context 更高效的工具结果

在处理大型数据集时，智能体可以在代码中过滤和转换结果，然后再返回它们。考虑获取一份有 10,000 行的电子表格：

```plaintext
// Without code execution - all rows flow through context
TOOL CALL: gdrive.getSheet(sheetId: 'abc123')
        → returns 10,000 rows in context to filter manually

// With code execution - filter in the execution environment
const allRows = await gdrive.getSheet({ sheetId: 'abc123' });
const pendingOrders = allRows.filter(row => 
  row["Status"] === 'pending'
);
console.log(`Found ${pendingOrders.length} pending orders`);
console.log(pendingOrders.slice(0, 5)); // Only log first 5 for review
```

智能体看到的是 5 行而不是 10,000 行。类似模式也适用于聚合、跨多个数据源的 join，或提取特定字段——都不必膨胀 context window。

#### 更强大、对 context 更高效的控制流

循环、条件判断和错误处理可以用熟悉的代码模式完成，而不必把一次次单独的工具调用串起来。例如，如果你需要在 Slack 中收到部署通知，智能体可以写成：

```plaintext
let found = false;
while (!found) {
  const messages = await slack.getChannelHistory({ channel: 'C123456' });
  found = messages.some(m => m.text.includes('deployment complete'));
  if (!found) await new Promise(r => setTimeout(r, 5000));
}
console.log('Deployment notification received');
```

这种方法比在智能体循环中交替进行 MCP 工具调用和 sleep 命令更高效。

此外，能够写出随后被执行的条件树，还可以节省 “time to first token” 延迟：智能体不必等待模型去评估一个 if 语句，而可以把这件事交给代码执行环境。

### 保护隐私的操作

当智能体结合 MCP 使用代码执行时，中间结果默认留在执行环境中。这样，智能体只看到你显式 log 或返回的内容，意味着你不希望与模型分享的数据可以在工作流中流动，却从不进入模型的 context。

对于更敏感的工作负载，智能体 harness 可以自动对敏感数据做 tokenize。例如，假设你需要把电子表格中的客户联系方式导入 Salesforce。智能体写下：

```plaintext
const sheet = await gdrive.getSheet({ sheetId: 'abc123' });
for (const row of sheet.rows) {
  await salesforce.updateRecord({
    objectType: 'Lead',
    recordId: row.salesforceId,
    data: { 
      Email: row.email,
      Phone: row.phone,
      Name: row.name
    }
  });
}
console.log(`Updated ${sheet.rows.length} leads`);
```

MCP 客户端会拦截数据，并在其到达模型之前对 PII 做 tokenize：

```plaintext
// What the agent would see, if it logged the sheet.rows:
[
  { salesforceId: '00Q...', email: '[EMAIL_1]', phone: '[PHONE_1]', name: '[NAME_1]' },
  { salesforceId: '00Q...', email: '[EMAIL_2]', phone: '[PHONE_2]', name: '[NAME_2]' },
  ...
]
```

然后，当数据在另一次 MCP 工具调用中被分享时，再通过 MCP 客户端中的查找做 untokenize。真实的电子邮箱、电话号码和姓名从 Google Sheets 流向 Salesforce，但从不经过模型。这可以防止智能体意外记录或处理敏感数据。你也可以用它来定义确定性的安全规则，选择数据可以流向何处、从何处而来。

### 状态持久化与 skills

结合文件系统访问的代码执行，让智能体可以在多次操作之间保持状态。智能体可以把中间结果写入文件，从而恢复工作并跟踪进度：

```plaintext
const leads = await salesforce.query({ 
  query: 'SELECT Id, Email FROM Lead LIMIT 1000' 
});
const csvData = leads.map(l => `${l.Id},${l.Email}`).join('\n');
await fs.writeFile('./workspace/leads.csv', csvData);

// Later execution picks up where it left off
const saved = await fs.readFile('./workspace/leads.csv', 'utf-8');
```

智能体也可以把自己的代码持久化为可复用函数。一旦智能体为某项任务开发出可用代码，它就可以保存该实现以供将来使用：

```plaintext
// In ./skills/save-sheet-as-csv.ts
import * as gdrive from './servers/google-drive';
export async function saveSheetAsCsv(sheetId: string) {
  const data = await gdrive.getSheet({ sheetId });
  const csv = data.map(row => row.join(',')).join('\n');
  await fs.writeFile(`./workspace/sheet-${sheetId}.csv`, csv);
  return `./workspace/sheet-${sheetId}.csv`;
}

// Later, in any agent execution:
import { saveSheetAsCsv } from './skills/save-sheet-as-csv';
const csvPath = await saveSheetAsCsv('abc123');
```

这与 [Skills](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview) 的概念密切相关：Skills 是可复用的指令、脚本和资源文件夹，用于提升模型在专门任务上的表现。为这些已保存的函数添加一个 SKILL.md 文件，就能创建模型可以引用和使用的结构化 skill。随着时间推移，这能让你的智能体积累一套更高层的能力工具箱，演化出它最有效工作所需的脚手架。

需要注意的是，代码执行本身也会引入复杂度。运行智能体生成的代码需要一个安全的执行环境，并配备适当的 [sandboxing](https://www.anthropic.com/engineering/claude-code-sandboxing)、资源限制和监控。这些基础设施要求增加了运维开销和安全考量，而直接工具调用则没有这些成本。代码执行的好处——降低 token 成本、降低延迟、改善工具组合——应当与这些实现成本加以权衡。

## 总结

MCP 为智能体连接许多工具和系统提供了基础协议。然而，一旦连接的 servers 过多，工具定义和结果可能消耗过量 token，降低智能体效率。

尽管这里的许多问题看起来很新——context 管理、工具组合、状态持久化——它们在软件工程中已有已知解决方案。代码执行把这些既有模式应用到智能体上，让它们用熟悉的编程结构更高效地与 MCP servers 交互。如果你实现了这一方法，我们鼓励你与 [MCP 社区](https://modelcontextprotocol.io/community/communication)分享发现。

## 作者与致谢

### 致谢

本文由 Adam Jones 和 Conor Kelly 撰写。感谢 Jeremy Fox、Jerome Swannack、Stuart Ritchie、Molly Vorwerck、Matt Samuels 和 Maggie Vo 对草稿的反馈。
