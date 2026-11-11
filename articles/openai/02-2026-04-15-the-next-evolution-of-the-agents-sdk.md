---
title_en: The next evolution of the Agents SDK
title_zh: Agents SDK 的下一步演进
company: openai
date: 2026-04-15
url: https://openai.com/index/the-next-evolution-of-the-agents-sdk/
type: full
category: 框架与 SDK
tags:
  - Agents SDK
  - 沙箱
  - harness
  - MCP
  - Skills
  - 长时任务
---

# Agents SDK 的下一步演进

更新后的 Agents SDK 帮助开发者构建能够在受控沙箱环境中检查文件、运行命令、编辑代码，并处理长时程任务的智能体。

我们正在为 Agents SDK 引入新能力，为开发者提供易于上手、并且正确面向 OpenAI 模型构建的标准化基础设施：一个模型原生的 harness，让智能体可以在计算机上跨越文件与工具工作，再加上用于安全运行这些工作的原生沙箱执行。

例如，开发者可以给智能体一个受控工作区、明确的指令，以及它检查证据所需的工具：

```python
# pip install "openai-agents>=0.14.0"

import asyncio
import tempfile
from pathlib import Path

from agents import Runner
from agents.run import RunConfig
from agents.sandbox import Manifest, SandboxAgent, SandboxRunConfig
from agents.sandbox.entries import LocalDir
from agents.sandbox.sandboxes import UnixLocalSandboxClient


async def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        dataroom = Path(tmp) / "dataroom"
        dataroom.mkdir()
        (dataroom / "metrics.md").write_text(
            "# Annual metrics\n\n"
            "| Year | Revenue | Operating income | Operating cash flow |\n"
            "| --- | ---: | ---: | ---: |\n"
            "| FY2025 | $124.3M | $18.6M | $24.1M |\n"
            "| FY2024 | $98.7M | $12.4M | $17.9M |\n",
            encoding="utf-8",
        )

        agent = SandboxAgent(
            name="Dataroom Analyst",
            model="gpt-5.4",
            instructions="Answer using only files in data/. Cite source filenames.",
            default_manifest=Manifest(entries={"data": LocalDir(src=dataroom)}),
        )

        result = await Runner.run(
            agent,
            "Compare FY2025 revenue, operating income, and operating cash flow with FY2024.",
            run_config=RunConfig(
                sandbox=SandboxRunConfig(client=UnixLocalSandboxClient()),
            ),
        )

        print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
```

开发者需要的不只是最好的模型，还需要支持智能体如何检查文件、运行命令、编写代码，并在许多步骤中持续工作的系统。

今天已有的系统在团队从原型走向生产时各有取舍。与模型无关的框架很灵活，但并不能充分利用前沿模型的能力；模型提供商的 SDK 可以更贴近模型，但往往对 harness 的可见性不足；托管的智能体 API 可以简化部署，但会限制智能体运行的位置以及它们如何访问敏感数据。

（原文引用了参与测试新 SDK 的客户评价，请见原页面。）

## 更有能力的智能体循环 Harness

随着今天的发布，Agents SDK 的 harness 对处理文档、文件和系统的智能体变得更有能力。它现在具有可配置的记忆、感知沙箱的编排、类似 Codex 的文件系统工具，以及与前沿智能体系统中日益常见的原语的标准化集成。

这些原语包括通过 MCP 使用工具、通过 skills 进行渐进式披露、通过 AGENTS.md 提供自定义指令、使用 shell 工具执行代码、使用 apply patch 工具编辑文件，等等。该 harness 将持续纳入新的智能体模式与原语，让开发者把更少时间花在核心基础设施更新上，把更多时间花在使智能体有用的领域逻辑上。

Harness 还通过使执行方式与这些模型表现最佳的方式对齐，帮助开发者释放更多前沿模型能力。这让智能体更接近模型的自然运行模式，从而提高复杂任务上的可靠性与性能——尤其当工作是长时运行的，或需要跨多样工具与系统协调时。

此外，我们意识到每个产品都是独特的，很少能整齐地套进一个模子。我们把 Agents SDK 设计为支持这种多样性。开发者得到一个即开即用又灵活的 harness——容易适配到自己的技术栈——包括工具使用、记忆和沙箱环境。

## 原生沙箱执行

更新后的 Agents SDK 原生支持沙箱执行，因此智能体可以在受控的计算机环境中运行，并拥有任务所需的文件、工具和依赖。

许多有用的智能体需要一个可以安全读写文件、安装依赖、运行代码和使用工具的工作区。原生沙箱支持开箱即用地提供这一执行层，而不必迫使开发者自行拼凑。

开发者可以自带沙箱，或使用对 Blaxel、Cloudflare、Daytona、E2B、Modal、Runloop 和 Vercel 的内置支持。

为使这些环境在提供商之间可移植，SDK 还引入 Manifest 抽象来描述智能体的工作区。开发者可以挂载本地文件、定义输出目录，并从包括 AWS S3、Google Cloud Storage、Azure Blob Storage 和 Cloudflare R2 在内的存储提供商引入数据。

这给开发者一种从本地原型到生产部署、一致地塑造智能体环境的方式。它也给模型一个可预测的工作区：到哪里找输入、到哪里写输出，以及如何在长时任务中保持工作有序。

## 把 Harness 与计算分离，以获得安全、持久与规模

智能体系统的设计应当假定会遇到提示注入与数据外泄尝试。把 harness 与计算分离，有助于把凭证排除在模型生成的代码所执行的环境之外。

它也使持久执行成为可能。当智能体状态被外置时，丢失一个沙箱容器并不意味着丢失这次运行。借助内置的快照与再水合（rehydration），如果原环境失败或过期，Agents SDK 可以在新容器中恢复智能体状态，并从最后一个检查点继续。

最后，它让智能体更可扩展。智能体运行可以使用一个或多个沙箱，仅在需要时调用沙箱，把子智能体路由到隔离环境，并跨容器并行化工作以加快执行。

## 定价与可用性

这些新的 Agents SDK 能力通过 API 向所有客户正式提供，并使用基于 tokens 与工具使用的标准 API 定价。

## 下一步

在继续发展 Agents SDK 的过程中，我们将不断扩展开发者可以用它构建的东西，使把更有能力的智能体带入生产所需的定制基础设施更少，同时保留开发者把智能体融入自有环境所需的灵活性与控制力。

新的 harness 与沙箱能力首先在 Python 中推出，TypeScript 支持计划在后续发布。我们也在努力把包括 code mode 和子智能体在内的更多智能体能力带到 Python 与 TypeScript。

此外，我们希望随着时间把更广泛的智能体生态连接起来，支持更多沙箱提供商、更多集成，以及更多让开发者把 SDK 接入他们已在使用的工具与系统的方式。
