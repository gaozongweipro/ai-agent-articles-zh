---
title_en: "Unlocking the Codex harness: how we built the App Server"
title_zh: 解锁 Codex Harness：我们如何构建 App Server
company: openai
date: 2026-02-04
url: https://openai.com/index/unlocking-the-codex-harness/
type: full
category: 编码 Agent
tags:
  - Codex
  - harness
  - MCP
  - 编码 Agent
  - 沙箱
---

# 解锁 Codex Harness：我们如何构建 App Server

作者：Celia Chen，技术团队成员

OpenAI 的编码智能体 Codex 存在于许多不同界面：Web 应用、CLI、IDE 扩展，以及新的 Codex macOS 应用。在底层，它们都由同一个 Codex harness 驱动——即支撑所有 Codex 体验的智能体循环与逻辑。它们之间的关键纽带是什么？是 Codex App Server，一个对客户端友好的、双向的 JSON-RPC API。

在这篇文章中，我们将介绍 Codex App Server；分享迄今为止关于把 Codex 能力带入你的产品、以帮助用户增强工作流的最佳实践。我们将介绍 App Server 的架构与协议，以及它如何与不同的 Codex 界面集成，还有关于如何利用 Codex 的提示——无论你想把它变成代码审查者、SRE 智能体，还是编程助手。

## App Server 的缘起

在深入架构之前，了解 App Server 的背景会有帮助。最初，App Server 是在多种产品中复用 Codex harness 的一种实用方式，并逐渐演变成我们的标准协议。

Codex CLI 一开始是 TUI（终端用户界面），意味着通过终端访问 Codex。当我们构建 VS Code 扩展（一种对 IDE 更友好的与 Codex 智能体交互的方式）时，需要一种使用同一 harness 的方式，以便从 IDE UI 驱动同一智能体循环，而不必重新实现它。这意味着要支持超出请求/响应的丰富交互模式，例如探索工作区、在智能体推理时流式传输进度，以及发出 diffs。我们首先尝试把 Codex 暴露为 MCP 服务器，但要以对 VS Code 有意义的方式维持 MCP 语义被证明很困难。于是我们引入了一个镜像 TUI 循环的 JSON-RPC 协议，它成为了 App Server 非正式的第一个版本。当时我们并未预期其他客户端会依赖 App Server，因此它并未被设计为稳定 API。

随着随后几个月 Codex 采用的增长，内部团队和外部合作伙伴希望能在自己的产品中嵌入同一 harness，以加速用户的软件开发工作流。例如，JetBrains 和 Xcode 希望获得 IDE 级的智能体体验，而 Codex 桌面应用需要并行编排许多 Codex 智能体。这些需求推动我们设计一个我们的产品和合作伙伴集成都能随时间安全依赖的平台面。它需要易于集成并且向后兼容，意味着我们可以演进协议而不破坏现有客户端。

接下来，我们将介绍我们如何设计架构和协议，以便不同客户端可以使用同一个 harness。

## Codex harness 内部

首先，让我们放大看看 Codex harness 内部有什么，以及 Codex App Server 如何把它暴露给客户端。在上一篇 Codex 博文中，我们拆解了编排用户、模型与工具之间交互的核心智能体循环。这是 Codex harness 的核心逻辑，但完整体验还有更多：

1. 线程生命周期与持久化。线程是用户与智能体之间的一次 Codex 对话。Codex 创建、恢复、分叉和归档线程，并持久化事件历史，以便客户端可以重新连接并渲染一致的时间线。

2. 配置与认证。Codex 加载配置、管理默认值，并运行如「用 ChatGPT 登录」的认证流程，包括凭证状态。

3. 工具执行与扩展。Codex 在沙箱中执行 shell/文件工具，并接入 MCP 服务器和 skills 等集成，使它们能在一致的策略模型下参与智能体循环。

我们这里提到的所有智能体逻辑，包括核心智能体循环，都位于 Codex CLI 代码库中称为「Codex core」的部分。Codex core 既是存放所有智能体代码的库，也是可以启动以运行智能体循环并管理一个 Codex 线程（对话）持久化的运行时。

要发挥作用，Codex harness 需要能被客户端访问。这正是 App Server 的用武之地。

App Server 既是客户端与服务器之间的 JSON-RPC 协议，也是托管 Codex core 线程的长生命周期进程。从原文示意图可以看到，一个 App Server 进程有四个主要组件：stdio 读取器、Codex 消息处理器、线程管理器，以及 core 线程。线程管理器为每个线程启动一个 core session，然后 Codex 消息处理器直接与每个 core session 通信，以提交客户端请求并接收更新。

一个客户端请求可以产生许多事件更新，正是这些详细事件使我们能在 App Server 之上构建丰富的 UI。此外，stdio 读取器和 Codex 消息处理器充当客户端与 Codex core 线程之间的翻译层。它们把客户端 JSON-RPC 请求翻译成 Codex core 操作，监听 Codex core 的内部事件流，然后把那些低层事件转换成一小套稳定的、对 UI 就绪的 JSON-RPC 通知。

客户端与 App Server 之间的 JSON-RPC 协议是完全双向的。一次典型的线程包含一个客户端请求和许多服务器通知。此外，当智能体需要输入（例如审批）时，服务器可以发起请求，然后暂停该轮直到客户端响应。

## 对话原语

接下来，我们将拆解对话原语，即 App Server 协议的构建块。为智能体循环设计 API 很棘手，因为用户/智能体交互不是简单的请求/响应。一次用户请求可以展开为客户端需要忠实表示的结构化动作序列：用户输入、智能体的增量进度、沿途产生的工件（例如 diffs）。为使该交互流易于集成并在各种 UI 上保持韧性，我们落在了三个具有清晰边界和生命周期的核心原语上：

1. Item（条目）：Item 是 Codex 中输入/输出的原子单位。条目是有类型的（例如用户消息、智能体消息、工具执行、审批请求、diff），并且每一个都有明确的生命周期：

- 条目开始时的 `item/started`
- 对可流式条目，可选的 `item/*/delta` 事件随内容流入
- 条目以终端载荷最终确定时的 `item/completed`

这一生命周期让客户端可以在 `started` 时立即开始渲染，在 `delta` 上流动增量更新，并在 `completed` 时定稿。

2. Turn（轮次）：一轮是由用户输入发起的一单位智能体工作。它在客户端提交输入（例如「运行测试并总结失败」）时开始，在智能体完成该输入的输出时结束。一轮包含一系列表示中间步骤和沿途输出的条目。

3. Thread（线程）：线程是用户与智能体之间进行中的 Codex 会话的持久容器。它包含多轮。线程可以被创建、恢复、分叉和归档。线程历史被持久化，以便客户端可以重新连接并渲染一致的时间线。

原文用简化图展示了客户端与智能体之间由这些原语表示的对话。

在对话开始时，客户端和服务器需要完成 `initialize` 握手。客户端必须在任何其他方法之前发送单个 `initialize` 请求，服务器用响应确认。这让服务器有机会公布能力，并让双方在真正工作开始之前就协议版本、功能开关和默认值达成一致。下面是来自 OpenAI VS Code 扩展的示例载荷：

```json
{
  "method": "initialize",
  "id": 0,
  "params": {
    "clientInfo": {
      "name": "codex_vscode",
      "title": "Codex VS Code Extension",
      "version": "0.1.0"
    }
  }
}
```

服务器返回示例：

```json
{
  "id": 0,
  "result": {
    "userAgent": "codex_vscode/0.94.0-alpha.7 (Mac OS 26.2.0; arm64) vscode/2.4.22 (codex_vscode; 0.1.0)"
  }
}
```

当客户端发出新请求时，它将首先创建线程，然后创建一轮。服务器会发回进度通知（`thread/started` 和 `turn/started`）。它也会把登记为条目的输入发回，例如这里的用户消息。

工具调用也会作为条目发回客户端。此外，服务器可能在运行某个动作之前通过发送服务器请求来征求客户端审批。审批会暂停该轮，直到客户端回复「允许」或「拒绝」。原文展示了这一审批流在 VS Code 扩展中的样子。

最后，服务器发送智能体消息，然后用 `turn/completed` 结束该轮。智能体消息的 delta 事件会流式传回消息片段，直到消息以 `item/completed` 定稿。

图中的消息为可读性做了简化。若想查看完整一轮的 JSON，可以从 Codex CLI 仓库运行测试客户端：

```bash
codex debug app-server send-message-v2 "run tests and summarize failures"
```

## 与客户端集成

现在看看不同客户端界面如何通过 App Server 嵌入 Codex。我们将介绍三种模式：本地应用与 IDE、Codex Web 运行时，以及 TUI。

在所有三种模式中，传输都是基于 stdio 的 JSON-RPC（JSONL）。JSON-RPC 使在你选择的语言中构建客户端绑定变得直接。Codex 界面和合作伙伴集成已在包括 Go、Python、TypeScript、Swift 和 Kotlin 在内的语言中实现了 App Server 客户端。对于 TypeScript，你可以通过运行以下命令，直接从 Rust 协议生成定义：

```bash
codex app-server generate-ts
```

对其它语言，你可以生成 JSON Schema 包并送入你偏好的代码生成器：

```bash
codex app-server generate-json-schema
```

### 本地应用与 IDE

本地客户端通常打包或获取特定平台的 App Server 二进制，把它作为长生命周期的子进程启动，并保持一条双向的 stdio 通道用于 JSON-RPC。例如在我们的 VS Code 扩展和桌面应用中，发布的产物包含特定平台的 Codex 二进制，并固定到经过测试的版本，以便客户端始终运行我们验证过的精确版本。

并非每一种集成都能频繁发布客户端更新。一些像 Xcode 这样的合作伙伴通过保持客户端稳定、并在需要时指向更新的 App Server 二进制，来解耦发布周期。这样它们可以采用服务器端改进（例如 Codex core 中更好的自动压缩，或新支持的配置键），并在不等待客户端发布的情况下推出错误修复。App Server 的 JSON-RPC 表面被设计为向后兼容，因此较旧的客户端可以安全地与较新的服务器通信。

### Codex Web

Codex Web 使用 Codex harness，但在容器环境中运行它。工作进程会开通一个带有检出工作区的容器，在其中启动 App Server 二进制，并维持一条长生命周期的、基于 stdio 的 JSON-RPC 通道。运行在用户浏览器标签中的 Web 应用通过 HTTP 和 SSE 与 Codex 后端通信，后者流式传输由工作进程产生的任务事件。这使浏览器端 UI 保持轻量，同时仍在桌面和 Web 上提供一致的运行时。

因为 Web 会话是短暂的（标签关闭、网络断开），Web 应用不能成为长时任务的事实来源。把状态和进度保留在服务器上，意味着即使标签消失，工作仍能继续。流式协议和保存的线程会话使新会话容易重新连接、从中断处继续，并在不必在客户端重建状态的情况下赶上进度。

### TUI / Codex CLI

历史上，TUI 是「原生」客户端，与智能体循环运行在同一进程中，直接与 Rust 核心类型对话，而不是通过 app-server 协议。这使早期迭代很快，但也使 TUI 成为一种特殊界面。

现在 App Server 已经存在，我们计划把 TUI 重构为使用它，使其行为像任何其他客户端：启动一个 App Server 子进程，通过 stdio 说 JSON-RPC，并渲染相同的流式事件和审批。这解锁了 TUI 可以连接到运行在远程机器上的 Codex 服务器的工作流，使智能体靠近计算，即使笔记本休眠或断开仍能继续工作，同时仍在本地提供实时更新和控制。

## 选择正确的协议

Codex App Server 将是我们今后维护的一等集成方法，但也有其他功能更有限的方法。默认情况下，我们建议客户端使用 Codex App Server 与 Codex 集成，但值得看看不同集成方法及其利弊。以下是驱动 Codex 的最常见方式，以及各自可能适合的时机。

### JSON-RPC 协议

#### 把 Codex 作为 MCP 服务器

运行 `codex mcp-server`，并从任何支持 stdio 服务器的 MCP 客户端（例如 OpenAI Agents SDK）连接。如果你已经有基于 MCP 的工作流，并希望把 Codex 作为可调用工具来调用，这是一个好选择。缺点是你只得到 MCP 所暴露的部分，因此依赖更丰富会话语义（例如 diff 更新）的 Codex 特定交互，可能无法干净地映射到 MCP 端点。

#### 跨提供商的智能体 harness 协议

一些生态提供可面向多个模型提供商和运行时的可移植接口。如果你想要一种协调多个智能体的抽象，这可能是好选择。权衡是这些协议往往收敛到能力的公共子集，这可能使更丰富的交互更难表示，尤其当提供商特定的工具和会话语义很重要时。这一领域变化很快，我们预期随着我们找出表示真实世界智能体工作流的最佳原语（skills 就是一个好例子），会有更多共同标准出现。

#### Codex App Server

当你希望把完整的 Codex harness 作为稳定、对 UI 友好的事件流暴露出来时，选择 App Server。你既能获得智能体循环的完整功能，也能获得「用 ChatGPT 登录」、模型发现和配置管理等支撑功能。主要成本是集成工作，因为你需要在自己的语言中构建客户端侧的 JSON-RPC 绑定。不过在实践中，如果你把 JSON schema 和文档提供给 Codex，它能够承担大量繁重工作。与我们合作的许多团队能够很快做出可用的集成。

### 嵌入 Codex 的其他方式

#### Codex Exec

一种轻量、可脚本化的 CLI 模式，用于一次性任务和 CI 运行。它适合自动化和流水线：你希望一条命令非交互地运行到完成，为日志流式输出结构化结果，并以清晰的成功或失败信号退出。

#### Codex SDK

一个 TypeScript 库，用于从你自己的应用中以编程方式控制本地 Codex 智能体。当你想要用于服务端工具和工作流的原生库接口、而不构建单独的 JSON-RPC 客户端时，它最合适。由于它比 App Server 更早发布，目前支持的语言更少、表面更小。如果有开发者兴趣，我们可能会增加封装 App Server 协议的额外 SDK，以便团队不必编写 JSON-RPC 绑定就能覆盖更多 harness 表面。

## 向前推进

在这篇文章中，我们分享了如何着手为与智能体交互设计新标准，以及如何把 Codex harness 变成稳定、对客户端友好的协议。我们介绍了 App Server 如何暴露 Codex core、让客户端驱动完整的智能体循环，并为一包括 TUI、本地 IDE 集成和 Web 运行时在内的广泛界面提供动力。

如果这激发了你把 Codex 集成进自己工作流的想法，值得试一试 App Server。全部源代码位于 Codex CLI 开源仓库。欢迎分享反馈和功能请求。我们兴奋地期待你的声音，并继续让智能体对每个人都更加可及。

## 脚注

1. 我们使用一种「JSON-RPC lite」变体：它保留请求/响应/通知的形态，但省略 `"jsonrpc": "2.0"` 头，并以 stdio 上的 JSONL 而不是严格的 JSON-RPC 2.0 来分帧。

2. 在托管设置中，「stdio」指容器内 app-server 的 stdin/stdout。这些流常常通过持久网络连接（例如类似 WebSocket）隧道到容器运行时——因此即便不是字面意义上的本地管道，其行为仍像 stdio。
