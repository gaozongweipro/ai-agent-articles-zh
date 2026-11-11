---
title_en: "One Agent Development Kit, five languages"
title_zh: 一个 Agent Development Kit，五种语言
company: google
date: 2026-10-13
url: https://cloud.google.com/blog/topics/developers-practitioners/one-agent-development-kit-five-languages/
type: full
category: 框架与 SDK
tags:
  - ADK
  - A2A
  - MCP
  - 框架与 SDK
  - 多 Agent
---

# 一个 Agent Development Kit，五种语言

当我们谈论智能体时，并不必然意味着我们在谈论 Python。在今天的现代生态中，一个智能体可能作为 Cloud Run 上的高并发 Go 微服务运行，或生活在调用 Chrome 端侧模型的浏览器标签中。然而许多智能体框架假定只有 Python 技术栈。这一假定迫使团队要么仅为智能体工作负载启动一个 Python 服务，要么在自己的语言中从零构建智能体编排逻辑。

Google 的 Agent Development Kit（ADK）通过覆盖 Python、Go、TypeScript、Java 和 Kotlin 消除了这一权衡。ADK 的每个语言版本都从其自己的运行时和类型系统出发构建，同时共享统一架构，并通过开放协议实现互操作。

## 共享基础

选择一种语言并不会把你锁定在某种架构中：全部五种都支持相同的开放协议。ADK 在每一种语言中都包含 Model Context Protocol 客户端，因此作为 MCP 服务器暴露的自定义工具可以从其中任何一种立即调用。

对于多智能体系统，ADK 支持 Agent2Agent（A2A）协议，允许一个智能体通过 HTTP 与远程智能体通信。通过 A2A，用不同语言或框架编写的智能体可以互操作。

## 从智能体优先开始

要开始，运行一次性设置命令以检查你的 Google Cloud 认证、安装 CLI，然后在 Antigravity、Claude Code 或 Codex 等编码智能体中设置第一方 ADK skills：

```
uvx google-agents-cli setup
```

然后运行脚手架命令，生成一个带有 A2A 端点、以及面向 Cloud Run、Gemini Enterprise Agent Runtime 或 Google Kubernetes Engine（GKE）之部署配置的可工作项目：

```
# Scaffold an ADK project (use --agent adk for Python or --agent adk_go for Go)
agents-cli scaffold create my-go-agent \
  --agent adk_go \
  --deployment-target cloud_run \
  --region us-central1
```

ADK for Python 和 ADK for Kotlin 的仓库也在源码树中附带智能体构建 skills，而 `adk.dev/llms.txt` 资源为任何编码智能体提供全部五种语言的按需 API 文档。

编码智能体的 skills 为你的项目搭建脚手架，同时 MCP 和 A2A 连接全部五种语言运行时。

## 动手看每种 ADK

感受五种语言之间差异的最清晰方式，是在每一种中定义同一个天气工具，并看看其设计如何贴合该运行时。

### Python

在 ADK for Python 中，你不需要装饰器或 schema 构建器类。你把一个普通的 Python 函数传入 `tools` 参数，ADK 在启动时检查其签名、类型提示和 docstring，以自动构造工具声明和 Pydantic 参数 schema：

```python
from google.adk.agents.llm_agent import Agent

def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.

    Args:
        city (str): The name of the city for which to retrieve the weather report.
    """
    return {"status": "success", "report": f"Sunny and 72F in {city}."}

root_agent = Agent(
    name="weather_agent",
    model="gemini-3.8-flash",
    instruction="Answer questions about the weather in a city.",
    tools=[get_weather],
)
```

除快速原型之外，Python 是 ADK 的参考实现，提供最广泛的 Google Cloud 集成（BigQuery、Spanner、Bigtable）和模型适配器（Gemini、Anthropic、OpenAI、LiteLLM）。与 `adk eval` 或 `agents-cli eval run` 命令配对，其评估工具会在持续集成（CI）中对照黄金数据集为智能体轨迹打分，即使你的生产服务运行在另一种语言中，也能端到端测试整个系统。

### Go

虽然 Python 在实验和评估上领先，ADK for Go 则打中了生产后端工程的甜区。

一个 Go 工具函数接收 `agent.Context` 配置和一个强类型输入结构体。`functiontool.New` 函数使用 Go 泛型，从你的 `struct` 标签推断输入和输出 schema：

```go
type GetWeatherArgs struct {
    City string `json:"city" jsonschema:"The city to look up weather for."`
}
type GetWeatherResult struct {
    Report string `json:"report"`
}

func getWeather(_ agent.Context, args GetWeatherArgs) (GetWeatherResult, error) {
    return GetWeatherResult{Report: "Sunny and 72F in " + args.City}, nil
}

weatherTool, err := functiontool.New(functiontool.Config{
    Name:        "get_weather",
    Description: "Retrieves the current weather report for a city.",
}, getWeather)
```

因为 `functiontool.New` 对其处理函数的签名是泛型的，Go 编译器会在二进制运行之前验证你的函数是否匹配预期契约。

Go 也是 Python 之后第一个交付 ADK 2.0 Graph Workflow 运行时的语言。当你需要与 LLM 推理并列的确定性控制流时，`workflow.New` 函数把智能体和普通 Go 函数连成带有条件路由和并行步骤的有向图。

Go 真正突出的地方是在 Cloud Run 和 GKE 上的生产。编译后的 Go 智能体可以打包到大约 2 MiB 的 Google distroless 静态基础镜像上，没有语言虚拟机或沉重的依赖树。静态 Go 二进制在容器启动后立即绑定端口，跳过动态语言的模块导入以及 JVM 服务的 JAR 解包和 JIT 预热。

运行之后，Go 的并发模型自然适合智能体工作负载。每个 goroutine 以 2 KB 栈和很小的调度开销开始，因此单个实例可以复用数千个并发的流式请求和工具调用。ADK for Go 还开箱包含内置的 A2A 服务器处理器和 OpenTelemetry 追踪。

### TypeScript

TypeScript 在编译到 JavaScript 时会擦除类型注解，因此运行时反射不是选项。相反，ADK for TypeScript 与 Zod 配对。你把一个 `z.object(...)` schema 传给 `FunctionTool` 函数，TypeScript 从这一单一声明静态推断你的 `execute` 回调的参数类型：

```typescript
import { FunctionTool, LlmAgent } from "@google/adk";
import { z } from "zod";

const getWeatherTool = new FunctionTool({
  name: "get_weather",
  description: "Retrieves the current weather report for a city.",
  parameters: z.object({
    city: z.string().describe("The name of the city."),
  }),
  execute: async ({ city }) => {
    return { status: "success", report: `Sunny and 72F in ${city}.` };
  },
});

export const rootAgent = new LlmAgent({
  name: "weather_agent",
  model: "gemini-3.8-flash",
  instruction: "Answer questions about the weather in a city.",
  tools: [getWeatherTool],
});
```

你的运行时输入验证、发送给模型的 JSON Schema，以及 `execute` 回调内部的 IDE 自动完成，都来自同一个真相来源。

TypeScript 也运行在 ADK 2.0 Graph Workflow 引擎上，并提供独立的浏览器包。除了 Node.js 服务，你还可以使用 WebMCP 做页面级工具、并用 Chrome 的端侧 Prompt API，直接在浏览器标签中运行 ADK 智能体。

### Java

对已经标准化使用 Maven、Gradle 和 Spring Boot 的团队，ADK for Java 可以直接接入。你为方法参数添加 `@Schema` 注解，并用流畅的 `LlmAgent.builder()` API 组装智能体：

```java
public class WeatherTools {
  public static Map<String, String> getWeather(
      @Schema(name = "city", description = "The name of the city")
      String city) {
    return Map.of("status", "success", "report", "Sunny and 72F in " + city);
  }
}

LlmAgent agent = LlmAgent.builder()
    .name("weather_agent")
    .model("gemini-3.8-flash")
    .instruction("Answer questions about the weather in a city.")
    .tools(FunctionTool.create(WeatherTools.class, "getWeather"))
    .build();
```

在运行时，runner 通过 RxJava 以响应式方式流式传输智能体事件。对于本地测试和现有 JVM 应用，ADK for Java 提供 Maven Dev UI 插件，以及面向 Spring AI 和 LangChain4j 的第一方桥接。

### Kotlin

ADK for Kotlin 在构建时安全上立场鲜明。其 Kotlin Symbol Processing（KSP）编译器插件在构建时读取 `@Tool` 和 `@Param` 注解，并把工具 schema 直接发射进字节码：

```kotlin
class WeatherTools {
  @Tool(
    name = "get_weather",
    description = "Retrieves the current weather report for a city.",
  )
  suspend fun getWeather(
    @Param("The name of the city.") city: String
  ): Map<String, String> = mapOf("status" to "success", "report" to "Sunny and 72F in $city")
}

val agent = LlmAgent(
  model = Gemini("gemini-3.8-flash"),
  name = "weather_agent",
  instruction = Instruction("Answer questions about the weather in a city."),
  tools = WeatherTools().generatedTools(),
)
```

如果工具签名使用了不支持的类型，或在非空参数上声明了默认值，你的 Gradle 构建会立即失败，而不是在生产中出错。因为 `.generatedTools()` 函数使用零运行时反射，它能在 Android R8 shrinking 后存活。

这种零反射设计使在 Android 上本地运行整个智能体循环成为可能。它提供 JVM 服务器支持，包括 Spring AI 桥接和实验性的 ADK 2.0 图工作流。在端侧，ADK for Kotlin 与用于工具调用的 LiteRT-LM 以及用于文本生成的 ML Kit（Gemini Nano）集成。它还与用于本地状态的 Room 和 AppSearch，以及用于操作系统级动作的 Android AppFunctions 一起工作，全部无需网络连接。

## 没有妥协的选择

ADK 中有五种原生语言，意味着你不必为整个组织挑选单一运行时。因为每个版本的 ADK 都说 MCP 和 A2A，系统的每个组件都可以使用最适合它的语言。

你用 Google 的 ADK 用过哪些语言构建智能体？欢迎在 X、LinkedIn 或 Bluesky 上告诉我们你正在运行的技术栈。
