# 面向 AI 智能体的有效 Context Engineering

- 英文标题：Effective context engineering for AI agents
- 中文标题：面向 AI 智能体的有效 Context Engineering
- 发布日期：2025-09-29
- 原文链接：https://www.anthropic.com/research/effective-context-engineering-for-ai-agents
- 翻译类型：全文翻译

---

在应用 AI 领域，prompt engineering 成为关注焦点数年之后，一个新术语开始受到重视：**context engineering**。用语言模型构建系统，正越来越少地关乎为 prompts 找到正确的措辞，而更多地关乎回答一个更广阔的问题：“怎样配置 context，最有可能产生我们希望模型表现出的行为？”

**Context** 指的是在从大语言模型（LLM）采样时被包含进去的那一组 tokens。眼前的**工程问题**是：在 LLM 固有约束下，优化这些 tokens 的效用，以持续达成期望结果。有效驾驭 LLM 往往需要*以 context 来思考*——换句话说：考虑在任意时刻 LLM 可获得的整体状态，以及该状态可能产生怎样的潜在行为。

本文将探讨正在兴起的 context engineering 这门技艺，并为构建可引导、有效的智能体提供一种更精细的心智模型。

## Context engineering 与 prompt engineering

在 Anthropic，我们将 context engineering 视为 prompt engineering 的自然演进。Prompt engineering 指的是为获得最优结果而撰写和组织 LLM 指令的方法（概述与有用策略见[我们的文档](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview)）。**Context engineering** 指的是在 LLM 推理过程中策划并维护最优 token（信息）集合的一组策略，包括除 prompts 之外可能进入该集合的所有其他信息。

在用 LLM 做工程的早期，prompting 是 AI 工程工作中最大的组成部分，因为日常聊天之外的大多数用例，都需要针对一次性分类或文本生成任务优化过的 prompts。顾名思义，prompt engineering 的主要焦点是如何写出有效的 prompts，尤其是 system prompts。然而，当我们转向工程化更能跨多轮推理、在更长周期上运作的智能体时，我们需要管理整个 context 状态的策略（系统指令、工具、[Model Context Protocol](https://modelcontextprotocol.io/docs/getting-started/intro)（MCP）、外部数据、消息历史等）。

在循环中运行的智能体会生成越来越多*可能*与下一轮推理相关的数据，而这些信息必须被周期性地精炼。Context engineering 就是从那不断演化的可能信息宇宙中，策划什么将进入有限 context window 的[艺术与科学](https://x.com/karpathy/status/1937902205765607626?lang=en)。

（原文配图：prompt engineering 与 context engineering 的对比。）

与撰写 prompt 这一离散任务不同，context engineering 是迭代的，策划阶段发生在我们每次决定向模型传入什么的时候。

## 为何 context engineering 对构建有能力的智能体很重要

尽管 LLM 速度很快，也能管理越来越大的数据量，我们观察到，LLM 像人类一样，到了某个点就会失去焦点或陷入困惑。关于 needle-in-a-haystack 风格基准的研究揭示了 [context rot](https://research.trychroma.com/context-rot) 这一概念：随着 context window 中的 token 数量增加，模型从该 context 中准确召回信息的能力会下降。

虽然有些模型的退化比其他模型更平缓，但这一特性在所有模型上都出现。因此，context 必须被视为一种边际收益递减的有限资源。就像人类有[有限的工作记忆容量](https://journals.sagepub.com/doi/abs/10.1177/0963721409359277)一样，LLM 在解析大量 context 时会消耗一种 “attention budget（注意力预算）”。每一个新引入的 token 都会在某种程度上消耗这一预算，从而更加需要仔细策划提供给 LLM 的 tokens。

这种注意力稀缺源于 LLM 的架构约束。LLM 基于 [transformer 架构](https://arxiv.org/abs/1706.03762)，它使每个 token 都能在整个 context 中[关注每一个其他 token](https://huggingface.co/blog/Esmail-AGumaan/attention-is-all-you-need)。对于 n 个 tokens，这会产生 n² 个成对关系。

随着 context 长度增加，模型捕捉这些成对关系的能力被摊薄，从而在 context 大小与注意力焦点之间形成一种自然张力。此外，模型的注意力模式来自训练数据分布，其中较短序列通常比长序列更常见。这意味着模型对跨整个 context 的依赖关系经验更少，专门参数也更少。

[位置编码插值（position encoding interpolation）](https://arxiv.org/pdf/2306.15595) 等技术通过把更长序列适配到原先训练的较小 context，使模型能够处理更长序列，但在 token 位置理解上会有一定退化。这些因素造成的是一条表现梯度，而不是硬悬崖：模型在更长 context 上仍然高度有能力，但在信息检索和长程推理上的精度，可能弱于在较短 context 上的表现。

这些现实意味着，深思熟虑的 context engineering 对于构建有能力的智能体至关重要。

## 有效 context 的构成

鉴于 LLM 受有限注意力预算的约束，*好的* context engineering 意味着找到*尽可能小*的高信号 token 集合，以最大化达成某种期望结果的可能性。把这一实践落地说起来容易做起来难，但在接下来的部分中，我们将概述这一指导原则在 context 的不同组成部分中意味着什么。

**System prompts** 应当极其清晰，使用简单直接的语言，并在对智能体而言*正确的抽象高度（right altitude）*上呈现想法。正确的高度是介于两种常见失败模式之间的 Goldilocks 区间。在一个极端，我们看到工程师在 prompts 中硬编码复杂、脆弱的逻辑，以引出精确的智能体行为。这种方法会造成脆弱性，并随着时间增加维护复杂度。在另一个极端，工程师有时提供模糊的高层指导，未能给 LLM 提供关于期望输出的具体信号，或错误地假定存在共享 context。最优高度是一种平衡：足够具体以有效引导行为，同时又足够灵活，为模型提供强有力的启发式来引导行为。

（原文配图：在 context engineering 过程中校准 system prompt。）

在光谱的一端，我们看到脆弱的 if-else 硬编码 prompts；在另一端，我们看到过于笼统、或错误假定共享 context 的 prompts。

我们建议将 prompts 组织成不同部分（例如 `<background_information>`、`<instructions>`、`## Tool guidance`、`## Output description` 等），并使用 XML 标签或 Markdown 标题等技术来划分这些部分，尽管随着模型能力增强，prompts 的精确格式可能正变得不那么重要。

无论你决定如何组织 system prompt，都应当追求能完整勾勒期望行为的最小信息集。（注意：最小并不一定意味着短；你仍然需要预先给智能体足够的信息，以确保它遵循期望行为。）最好的做法是：先用现有最好的模型测试一份最小 prompt，看它在你的任务上表现如何，然后根据初始测试中发现的失败模式，加入清晰的指令和示例来改进表现。

**工具（Tools）** 使智能体能够与环境交互，并在工作过程中拉取新的、额外的 context。因为工具定义了智能体与其信息/动作空间之间的契约，极其重要的是：工具要促进效率，既通过返回对 token 高效的信息，也通过鼓励高效的智能体行为。

在 [Writing tools for AI agents – with AI agents](https://www.anthropic.com/engineering/writing-tools-for-agents) 中，我们讨论了构建对 LLM 易于理解、功能重叠最小的工具。类似于设计良好的代码库中的函数，工具应当是自包含的、对错误鲁棒的，并且就其预期用途而言极其清晰。输入参数同样应当是描述性的、无歧义的，并发挥模型固有的优势。

我们看到的最常见失败模式之一，是臃肿的工具集：覆盖了过多功能，或导致关于该用哪个工具的模糊决策点。如果一名人类工程师无法明确说出在给定情形下该用哪个工具，就不能指望 AI 智能体做得更好。正如后文将讨论的，为智能体策划一套最小可行工具集，也可以在长时间交互中带来更可靠的 context 维护与修剪。

提供示例，也就是 few-shot prompting，是一项我们继续强烈建议的著名最佳实践。然而，团队常常把一长串边界情况塞进 prompt，试图阐明 LLM 在特定任务上应遵循的每一条可能规则。我们不建议这样做。相反，我们建议努力策划一组多样、典型的示例，有效刻画智能体的期望行为。对 LLM 而言，示例是“一图胜千言”。

我们对 context 不同组成部分（system prompts、工具、示例、消息历史等）的总体指导是：深思熟虑，让你的 context 信息丰富，但保持紧凑。现在让我们深入运行时动态检索 context。

## Context 检索与智能体式搜索

在 [Building effective AI agents](https://www.anthropic.com/research/building-effective-agents) 中，我们强调了基于 LLM 的工作流与智能体之间的差异。自那篇文章以来，我们逐渐采用了关于智能体的一个[简单定义](https://simonwillison.net/2025/Sep/18/agents/)：在循环中自主使用工具的 LLM。

在与客户合作的过程中，我们看到这一领域正在向这一简单范式收敛。随着底层模型能力增强，智能体的自主程度可以扩展：更聪明的模型使智能体能独立导航微妙的问题空间并从错误中恢复。

我们现在看到，工程师思考如何为智能体设计 context 的方式正在转变。如今，许多 AI-native 应用会采用某种基于嵌入的、在推理前进行的检索，以便为智能体呈现供其推理的重要 context。随着该领域转向更智能体化的方法，我们越来越多地看到团队用 “just in time（即时）” context 策略来增强这些检索系统。

与其预先处理所有相关数据，采用 “just in time” 方法构建的智能体会维护轻量标识符（文件路径、已存储的查询、网页链接等），并在运行时使用工具动态地把数据加载进 context。Anthropic 的智能体式编程方案 [Claude Code](https://www.anthropic.com/claude-code) 就使用这种方法，在大型数据库上进行复杂数据分析。模型可以编写有针对性的查询、存储结果，并利用 head 和 tail 等 Bash 命令分析大量数据，而从不把完整数据对象加载进 context。这种方法与人类认知相呼应：我们通常不会记住整部信息语料，而是引入文件系统、收件箱和书签等外部组织与索引系统，以便按需检索相关信息。

除了存储效率之外，这些引用的元数据还提供了一种高效精炼行为的机制，无论这种元数据是显式提供的还是直观的。对在文件系统中运作的智能体而言，`tests` 文件夹中一个名为 `test_utils.py` 的文件，其用途暗示与位于 `src/core_logic/` 中同名文件不同。文件夹层次、命名约定和时间戳都提供了重要信号，帮助人类和智能体理解如何以及何时使用信息。

让智能体自主导航并检索数据，也使渐进式披露（progressive disclosure）成为可能——换句话说，允许智能体通过探索逐步发现相关 context。每一次交互都会产生告知下一步决策的 context：文件大小暗示复杂度；命名约定暗示用途；时间戳可以作为相关性的代理。智能体可以一层一层地组装理解，只在工作记忆中保留必要内容，并利用笔记策略实现额外持久化。这种自我管理的 context window 使智能体聚焦于相关子集，而不是淹没在详尽但可能无关的信息中。

当然，这里有权衡：运行时探索比检索预先计算的数据更慢。不仅如此，还需要有主张、深思熟虑的工程，以确保 LLM 拥有有效导航其信息景观所需的正确工具和启发式。如果没有适当指导，智能体可能因误用工具、追逐死路，或未能识别关键信息而浪费 context。

在某些设置中，最有效的智能体可能采用混合策略：预先检索部分数据以换取速度，并自行决定是否进一步自主探索。“正确”自主程度的决策边界取决于任务。Claude Code 是采用这种混合模型的智能体：[CLAUDE.md](http://claude.md) 文件会在一开始就被直接放入 context，而 glob 和 grep 等原语使它能够导航环境并即时检索文件，有效绕过了过时索引和复杂语法树的问题。

混合策略可能更适合内容不那么动态的情境，例如法律或金融工作。随着模型能力提升，智能体设计将趋向于让智能的模型智能地行动，人工策划逐渐减少。鉴于该领域的快速进展，“做能奏效的最简单的事”很可能仍将是我们给在 Claude 之上构建智能体的团队的最好建议。

### 面向长周期任务的 context engineering

长周期任务要求智能体在动作序列中保持连贯性、context 和目标导向行为，而这些序列的 token 数量会超出 LLM 的 context window。对于跨越数十分钟到连续数小时工作的任务，例如大型代码库迁移或综合性研究项目，智能体需要专门技术来绕过 context window 大小的限制。

等待更大的 context windows 看起来或许是显而易见的策略。但在可预见的未来，无论大小如何，所有 context windows 都可能受到 context 污染和信息相关性问题的影响——至少在希望获得最强智能体表现的情形中是如此。为使智能体能够在延长的时间跨度上有效工作，我们开发了一些直接应对这些 context 污染约束的技术：compaction、结构化笔记，以及多智能体架构。

#### Compaction（压缩）

Compaction 是这样一种实践：在对话接近 context window 上限时，对其内容做摘要，并用该摘要重新开启一个新的 context window。Compaction 通常是 context engineering 中用于提升长期连贯性的第一根杠杆。其核心是以高保真方式提炼 context window 的内容，使智能体能够以最小的表现退化继续工作。

例如在 Claude Code 中，我们通过把消息历史传给模型来实现这一点，让模型总结并压缩最关键的细节。模型会保留架构决策、未解决的 bug 和实现细节，同时丢弃冗余的工具输出或消息。智能体随后可以带着这份压缩后的 context，加上最近访问的五个文件继续工作。用户获得连续性，而不必担心 context window 限制。

Compaction 的艺术在于选择保留什么、丢弃什么，因为过于激进的 compaction 可能导致丢失微妙但关键的 context，而其重要性往往要到后来才显现。对于实现 compaction 系统的工程师，我们建议在复杂的智能体 traces 上仔细调优你的 prompt。先最大化召回，确保你的 compaction prompt 捕获了 trace 中每一条相关信息，然后再迭代提高精度，剔除多余内容。

一个容易下手的多余内容例子是清除工具调用和结果——一旦某个工具已在消息历史深处被调用过，智能体为何还需要再次看到原始结果？最安全、最轻触的 compaction 形式之一就是工具结果清除，最近已作为 [Claude Developer Platform 上的一项功能](https://www.anthropic.com/news/context-management) 推出。

#### 结构化笔记（Structured note-taking）

结构化笔记，或称智能体记忆（agentic memory），是一种技术：智能体定期把笔记持久化到 context window 之外的记忆中。这些笔记会在稍后被拉回 context window。

这一策略以极小开销提供持久记忆。就像 Claude Code 创建一个待办清单，或你的定制智能体维护一个 NOTES.md 文件，这种简单模式使智能体能够跨复杂任务跟踪进度，维护在数十次工具调用中本会丢失的关键 context 和依赖。

[Claude 玩 Pokémon](https://www.twitch.tv/claudeplayspokemon) 展示了记忆如何在非编程领域改变智能体能力。该智能体在数千个游戏步骤中保持精确计数——跟踪诸如“在过去 1,234 步里我一直在 Route 1 训练我的 Pokémon，Pikachu 已向目标 10 级提升了 8 级”这样的目标。在没有关于记忆结构的任何 prompting 的情况下，它会绘制已探索区域的地图，记住已解锁的关键成就，并维护战斗策略的战略笔记，以帮助自己学习哪些攻击对不同对手最有效。

在 context 重置之后，智能体阅读自己的笔记，并继续数小时的训练序列或地下城探索。这种跨越摘要步骤的连贯性，使仅把全部信息保留在 LLM 的 context window 中所不可能实现的长周期策略成为可能。

作为我们 [Sonnet 4.5 发布](https://www.anthropic.com/effective-context-engineering-for-ai-agents) 的一部分，我们在 Claude Developer Platform 上以公开 beta 形式发布了[一个 memory tool](http://anthropic.com/news/context-management)，通过基于文件的系统，更容易在 context window 之外存储和查阅信息。这使智能体能够随时间建立知识库、跨 sessions 维护项目状态，并在不必把一切保留在 context 中的情况下引用先前工作。

#### 子智能体架构（Sub-agent architectures）

子智能体架构提供了绕过 context 限制的另一种方式。与其让一个智能体试图跨整个项目维护状态，专门的子智能体可以用干净的 context windows 处理聚焦的任务。主智能体用高层计划进行协调，而子智能体执行深入的技术工作，或使用工具寻找相关信息。每个子智能体可能会广泛探索，使用数万甚至更多 tokens，但只返回一份浓缩、提炼过的工作摘要（通常 1,000–2,000 tokens）。

这种方法实现了清晰的关注点分离——详细的搜索 context 被隔离在子智能体内部，而主导智能体聚焦于综合和分析结果。这一模式在 [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) 中有所讨论，在复杂研究任务上相对单智能体系统表现出显著改进。

在这些方法之间的选择取决于任务特征。例如：

- Compaction 为需要大量来回的任务保持对话流；
- 笔记法擅长有清晰里程碑的迭代开发；
- 多智能体架构适合复杂的研究与分析，在这些任务中并行探索会带来收益。

即使模型持续改进，在延长交互中保持连贯性的挑战，仍将是构建更有效智能体的核心。

## 结论

Context engineering 代表了我们如何用 LLM 构建系统的根本转变。随着模型能力增强，挑战不再只是打造完美的 prompt——而是在每一步都深思熟虑地策划哪些信息进入模型有限的注意力预算。无论你是在为长周期任务实现 compaction、设计对 token 高效的工具，还是让智能体即时探索其环境，指导原则都是相同的：找到最大化达成期望结果可能性的最小高信号 token 集合。

我们概述的这些技术将随着模型改进而继续演化。我们已经看到，更聪明的模型需要更少的规定性工程，从而使智能体能以更高自主性运作。但即使能力扩展，把 context 当作一种珍贵、有限的资源对待，仍将是构建可靠、有效智能体的核心。

今天就可以在 Claude Developer Platform 上开始 context engineering，并通过我们的 [memory and context management](https://platform.claude.com/cookbook/tool-use-memory-cookbook) cookbook 获取有用技巧和最佳实践。

## 作者与致谢

由 Anthropic Applied AI 团队撰写：Prithvi Rajasekaran、Ethan Dixon、Carly Ryan 和 Jeremy Hadfield，团队成员 Rafi Ayub、Hannah Moran、Cal Rueb 和 Connor Jennings 亦有贡献。特别感谢 Molly Vorwerck、Stuart Ritchie 和 Maggie Vo 的支持。
