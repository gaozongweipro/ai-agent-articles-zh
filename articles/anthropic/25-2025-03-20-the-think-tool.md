---
title_en: "The \"think\" tool: Enabling Claude to stop and think in complex tool use situations"
title_zh: “Think” 工具：让 Claude 在复杂工具使用场景中停下来思考
company: anthropic
date: 2025-03-20
updated: 2025-12-15
url: https://www.anthropic.com/research/claude-think-tool
type: full
category: 工具与协议
tags:
  - 工具调用
  - thinking
  - think tool
---

# “Think” 工具：让 Claude 在复杂工具使用场景中停下来思考

### Extended thinking 更新说明（2025 年 12 月 15 日）

自 extended thinking 最初发布以来，其能力已有提升。在大多数情况下，我们建议使用该功能，而不是专门的 think 工具。Extended thinking 能提供类似的收益——给 Claude 空间去推理复杂问题——同时具备更好的集成与性能。实现细节见我们的 extended thinking 文档。

---

在持续增强 Claude 复杂问题解决能力的过程中，我们发现了一种特别有效的方法：一个 “think” 工具，在复杂任务中为结构化思考提供专门空间。

这一简单却强大的技术——如下文将说明的，它不同于 Claude 新的 [extended thinking](https://www.anthropic.com/research/visible-extended-thinking) 能力（实现细节见 [extended thinking 文档](https://platform.claude.com/docs/en/build-with-claude/extended-thinking)）——显著提升了 Claude 的智能体式工具使用能力。这包括遵循政策、做出一致决策，以及处理多步骤问题，而且实现开销极小。

本文将探讨如何在不同应用中实现 “think” 工具，并基于经过验证的基准结果，为开发者提供实践指导。

## 什么是 “think” 工具？

通过 “think” 工具，我们让 Claude 在到达最终答案的过程中，可以加入一个额外的思考步骤——并且有专门为其预留的空间。

虽然听起来与 extended thinking 相似，但它们是不同的概念。Extended thinking 关注的是 Claude 在开始生成回复*之前*做的事情：Claude 会在采取行动前深入考虑并迭代其计划。“Think” 工具则是在 Claude 已经开始生成回复之后，增加一步停下来思考：它是否已经掌握了继续推进所需的全部信息。这在执行长链工具调用、或与用户进行长时间多轮对话时尤其有用。

因此，“think” 工具更适合这样的情形：仅凭用户查询，Claude 并没有制定回复所需的全部信息，而需要处理外部信息（例如工具调用结果中的信息）。Claude 用 “think” 工具进行的推理，不如 extended thinking 全面，而更聚焦于模型新发现的信息。

对于更简单的工具使用场景——例如非顺序的工具调用，或直接的指令遵循——我们建议使用 extended thinking。Extended thinking 也适用于编程、数学和物理等你不需要 Claude 调用工具的用例。“Think” 工具则更适合：Claude 需要调用复杂工具、在长链工具调用中仔细分析工具输出、在有详细指南的政策密集型环境中导航，或做出每一步都建立在前一步之上、且错误代价很高的顺序决策。

下面是使用来自 [τ-Bench](https://arxiv.org/abs/2406.12045) 的标准工具规范格式的示例实现：

```plaintext
{
  "name": "think",
  "description": "Use the tool to think about something. It will not obtain new information or change the database, but just append the thought to the log. Use it when complex reasoning or some cache memory is needed.",
  "input_schema": {
    "type": "object",
    "properties": {
      "thought": {
        "type": "string",
        "description": "A thought to think about."
      }
    },
    "required": ["thought"]
  }
}
```

## 在 τ-Bench 上的表现

我们使用 τ-bench（tau-bench）评估了 “think” 工具。这是一个综合性基准，用于测试模型在现实客服场景中使用工具的能力，而 “think” 工具是该评估标准环境的一部分。

τ-bench 评估 Claude 在以下方面的能力：

- 与模拟用户进行真实对话
- 始终如一地遵循复杂的客服智能体政策指南
- 使用多种工具访问和操作环境数据库

τ-bench 使用的主要评估指标是 pass^*k*，衡量的是：对于给定任务，*k* 次独立试验全部成功的概率，再对所有任务取平均。这不同于其他 LLM 评估中常见的 pass@*k* 指标（衡量 *k* 次试验中至少一次成功）。pass^*k* 评估的是一致性与可靠性——对客服应用而言，始终遵守政策是至关重要的品质。

### 表现分析

我们的评估比较了几种不同配置：

1. 基线（没有 “think” 工具，也没有 extended thinking 模式）
2. 仅使用 extended thinking 模式
3. 仅使用 “think” 工具
4. “Think” 工具加上优化过的 prompt（针对航空领域）

结果显示，当 Claude 3.7 在基准的 “airline”（航空）和 “retail”（零售）客服领域中有效使用 “think” 工具时，表现有显著提升：

- **航空领域**：“Think” 工具加上优化 prompt 在 pass^1 指标上达到 0.570，而基线仅为 0.370——相对提升 54%；
- **零售领域**：仅使用 “think” 工具达到 0.812，基线为 0.783。

（原文配图：Claude 3.7 Sonnet 在 Tau-Bench 评估 “airline” 领域四种不同配置下的折线图。）

Claude 3.7 Sonnet 在 Tau-Bench 评估 “airline” 领域四种不同配置下的表现。

## Claude 3.7 Sonnet 在 Tau-Bench 评估 “Airline” 领域上的表现

| 配置 | *k*=1 | *k*=2 | *k*=3 | *k*=4 | *k*=5 |
| --- | --- | --- | --- | --- | --- |
| "Think" + Prompt | 0.584 | 0.444 | 0.384 | 0.356 | 0.340 |
| "Think" | 0.404 | 0.254 | 0.186 | 0.140 | 0.100 |
| Extended thinking | 0.412 | 0.290 | 0.232 | 0.192 | 0.160 |
| Baseline | 0.332 | 0.206 | 0.148 | 0.116 | 0.100 |

四种不同配置下的评估结果。分数为比例。

航空领域的最佳表现，来自将 “think” 工具与一份优化 prompt 配对。该 prompt 给出了在分析客户请求时应使用的推理方法示例。下面是优化 prompt 的一个例子：

```plaintext
## Using the think tool

Before taking any action or responding to the user after receiving tool results, use the think tool as a scratchpad to:
- List the specific rules that apply to the current request
- Check if all required information is collected
- Verify that the planned action complies with all policies
- Iterate over tool results for correctness 

Here are some examples of what to iterate over inside the think tool:
<think_tool_example_1>
User wants to cancel flight ABC123
- Need to verify: user ID, reservation ID, reason
- Check cancellation rules:
  * Is it within 24h of booking?
  * If not, check ticket class and insurance
- Verify no segments flown or are in the past
- Plan: collect missing info, verify rules, get confirmation
</think_tool_example_1>

<think_tool_example_2>
User wants to book 3 tickets to NYC with 2 checked bags each
- Need user ID to check:
  * Membership tier for baggage allowance
  * Which payments methods exist in profile
- Baggage calculation:
  * Economy class × 3 passengers
  * If regular member: 1 free bag each → 3 extra bags = $150
  * If silver member: 2 free bags each → 0 extra bags = $0
  * If gold member: 3 free bags each → 0 extra bags = $0
- Payment rules to verify:
  * Max 1 travel certificate, 1 credit card, 3 gift cards
  * All payment methods must be in profile
  * Travel certificate remainder goes to waste
- Plan:
1. Get user ID
2. Verify membership level for bag fees
3. Check which payment methods in profile and if their combination is allowed
4. Calculate total: ticket price + any bag fees
5. Get explicit confirmation for booking
</think_tool_example_2>
```

特别有趣的是不同方法之间的比较。使用带优化 prompt 的 “think” 工具，显著优于 extended thinking 模式（后者与未经 prompt 引导的 “think” 工具表现相近）。仅使用 “think” 工具（不加 prompting）也优于基线，但仍不及优化方案。

“Think” 工具与优化 prompting 的组合以显著优势取得了最强表现，这很可能是因为基准中 [航空政策](https://github.com/sierra-research/tau-bench/blob/main/tau_bench/envs/airline/wiki.md) 部分的复杂度很高，模型从被给予如何 “think” 的示例中获益最多。

在零售领域，我们也测试了多种配置，以理解每种方法的具体影响。

（原文配图：Claude 3.7 Sonnet 在 Tau-Bench 评估 “retail” 领域三种不同配置下的折线图。）

Claude 3.7 Sonnet 在 Tau-Bench 评估 “retail” 领域三种不同配置下的表现。

## Claude 3.7 Sonnet 在 Tau-Bench 评估 “Retail” 领域上的表现

| 配置 | *k*=1 | *k*=2 | *k*=3 | *k*=4 | *k*=5 |
| --- | --- | --- | --- | --- | --- |
| "Think" + no prompt | 0.812 | 0.735 | 0.685 | 0.650 | 0.626 |
| Extended thinking | 0.770 | 0.681 | 0.623 | 0.581 | 0.548 |
| Baseline | 0.783 | 0.695 | 0.643 | 0.607 | 0.583 |

三种不同配置下的评估结果。分数为比例。

即使没有额外 prompting，“think” 工具也取得了最高的 pass^1 分数 0.812。[零售政策](https://github.com/sierra-research/tau-bench/blob/main/tau_bench/envs/retail/wiki.md) 相比航空领域明显更容易导航，Claude 仅仅通过拥有一个思考空间、无需进一步指导，就能有所提升。

### 来自 τ-Bench 分析的关键洞见

我们的细致分析揭示了若干模式，可以帮助你有效实现 “think” 工具：

1. **在困难领域中，prompting 非常重要。** 仅仅提供 “think” 工具或许就能带来一定提升，但将其与优化 prompting 配对，会在困难领域产生显著更好的结果。不过，更容易的领域可能仅凭能够使用 “think” 就能获益。
2. **跨试验的一致性有所改善。** 使用 “think” 带来的提升在 pass^k 上一直保持到 k=5，表明该工具帮助 Claude 更有效地处理了边界情况和异常场景。

## 在 SWE-Bench 上的表现

在评估 Claude 3.7 Sonnet 时，我们的 SWE-bench 设置中也加入了类似的 “think” 工具，为最终取得 0.623 的当时最先进分数做出了贡献。改编后的 “think” 工具定义如下：

```plaintext
{
  "name": "think",
  "description": "Use the tool to think about something. It will not obtain new information or make any changes to the repository, but just log the thought. Use it when complex reasoning or brainstorming is needed. For example, if you explore the repo and discover the source of a bug, call this tool to brainstorm several unique ways of fixing the bug, and assess which change(s) are likely to be simplest and most effective. Alternatively, if you receive some test results, call this tool to brainstorm ways to fix the failing tests.",
  "input_schema": {
    "type": "object",
    "properties": {
      "thought": {
        "type": "string",
        "description": "Your thoughts."
      }
    },
    "required": ["thought"]
  }
}
```

我们的实验（使用 “think” 工具 *n*=30 个样本，不使用 *n*=144 个样本）显示，单独加入该工具平均提升了 1.6% 的表现（Welch's *t*-test：*t*(38.89) = 6.71，*p* < .001，*d* = 1.47）。

## 何时使用 “think” 工具

基于这些评估结果，我们识别出 Claude 从 “think” 工具中获益最多的特定场景：

1. **工具输出分析。** 当 Claude 需要在行动前仔细处理先前工具调用的输出，并可能需要回溯其方法时；
2. **政策密集型环境。** 当 Claude 需要遵循详细指南并核实合规性时；以及
3. **顺序决策。** 当每一步行动都建立在前一步之上、且错误代价很高时（常见于多步骤领域）。

## 实现最佳实践

为了与 Claude 一起最大程度发挥 “think” 工具的作用，我们根据 τ-bench 实验推荐以下实现实践。

### 1. 带有领域特定示例的战略性 prompting

最有效的方法是提供关于何时以及如何使用 “think” 工具的清晰指令，例如用于 τ-bench 航空领域的那一份。针对你的具体用例提供示例，能显著提高模型使用 “think” 工具的有效性：

- 推理过程中期望的细节程度；
- 如何将复杂指令拆成可执行步骤；
- 处理常见场景的决策树；以及
- 如何检查是否已收集全部必要信息。

### 2. 把复杂指导放在 system prompt 中

我们发现，当关于 “think” 工具的指令较长和/或较复杂时，把它们放在 system prompt 中，比放在工具描述本身更有效。这种方法能提供更广阔的上下文，并帮助模型把思考过程更好地整合进其整体行为。

## 何时*不要*使用 “think” 工具

尽管 “think” 工具可以带来可观改进，它并不适用于所有工具使用用例，并且会增加 prompt 长度和输出 token。具体而言，我们发现 “think” 工具在以下用例中没有带来任何改进：

1. **非顺序的工具调用。** 如果 Claude 只需进行一次工具调用，或多次并行调用即可完成任务，加入 “think” 不太可能带来提升。
2. **简单的指令遵循。** 当 Claude 需要遵守的约束不多，且其默认行为已经足够好时，额外的 “think” 不太可能带来收益。

## 如何开始

“Think” 工具是对你的 Claude 实现的一个直接补充，只需几个步骤就能带来有意义的改进：

1. **在智能体式工具使用场景中测试。** 从有挑战性的用例开始——也就是 Claude 目前在政策合规、或长链工具调用中的复杂推理上感到困难的那些。
2. **加入工具定义。** 实现一个针对你的领域定制的 “think” 工具。所需代码极少，却能支持更结构化的推理。同时考虑在 system prompt 中加入何时以及如何使用该工具的指令，并附上与你的领域相关的示例。
3. **监控并改进。** 观察 Claude 在实践中如何使用该工具，并调整你的 prompts，以鼓励更有效的思考模式。

最好的一点是，加入这个工具在表现结果方面几乎没有下行风险。除非 Claude 决定使用它，否则它不会改变外部行为，也不会干扰你现有的工具或工作流。

## 结论

我们的研究表明，“think” 工具可以显著提升 Claude 3.7 Sonnet 在需要政策遵循、以及长链工具调用中的推理的复杂任务上的表现。[^1] “Think” 并非放之四海而皆准的方案，但对于正确的用例，它能以极小的实现复杂度带来可观收益。

我们期待看到你如何使用 “think” 工具，与 Claude 一起构建更有能力、更可靠、更透明的 AI 系统。

## 脚注

[^1]: 虽然我们的 τ-Bench 结果聚焦于 Claude 3.7 Sonnet 使用 “think” 工具后的提升，但实验表明 Claude 3.5 Sonnet (New) 在与 3.7 Sonnet 相同的配置下也能获得表现提升，说明这一改进可以推广到其他 Claude 模型。
