# 智能体记忆的组成

- 英文标题：The components of agent memory
- 中文标题：智能体记忆的组成
- 发布日期：2026-11-06
- 原文链接：https://www.anthropic.com/research/components-of-agent-memory
- 翻译类型：全文翻译

---

Søren Kierkegaard 写道，生命只能被*向后*理解，却必须被*向前*度过。在为 AI 智能体设计记忆时，我们遇到了类似的困境。

作为人类，我们在生活过程中持续编码记忆。[海马体](https://stanford.edu/~jlmcc/papers/McCMcNaughtonOReilly95.pdf)在其中扮演核心角色，在当下捕获体验，使记忆迅速形成并立即可用。但只有[部分体验](https://www.science.org/doi/10.1126/science.adk8261?referrer=https%3A%2F%2Fwww.google.com%2F)会被巩固为长期知识。

这种巩固中的许多似乎发生在我们的大脑离线时。当我们睡眠、以及在安静的[休息](https://www.nature.com/articles/s41467-018-06213-1)期间，海马体会重放我们最近的体验。这被认为会逐渐[提炼这些体验并把它们整合](https://www.nature.com/articles/s41593-019-0467-3)进新皮层——我们大脑中存储我们通常称为知识的大部分内容的部分。

智能体记忆可以使用类似的劳动分工。智能体在日志或 transcripts 中捕获其工作的大部分。Letta 和加州大学伯克利分校的研究人员提出了 [sleep-time compute](https://arxiv.org/abs/2504.13171)，作为一种让模型在交互之间的空闲时间重组现有 context 的方式。同样的想法可以帮助智能体通过反思日志来组织记忆，以修复错误或产生新的笔记和表征。这一过程常常被称为 [*dreaming*（做梦）](https://platform.claude.com/docs/en/managed-agents/dreams)（图 1）。（另见 [Google Research 的 SLEEP 框架](https://research.google/blog/the-sleep-framework-a-new-way-for-llms-to-retain-knowledge-in-continual-learning/)。）

我们发现，dreaming 一直是帮助我们给予 Claude 有效记忆的有用工具。本文将分享我们如何思考智能体记忆，并介绍我们用来探索智能体记忆的若干评估，包括 dreaming 的使用，以及每个组成部分对记忆组织的贡献。

（原文配图：session 之间的记忆层次示意图。从下到上：transcripts（可搜索的事件日志）、Claude 撰写的记忆笔记、wiki 等记忆表征，以及加载进每个 session 的注入 context。在标为 “Dreaming” 的框中，箭头从 transcripts 向上指向每一层，并在相邻上层之间双向运行。）

Claude 可以使用 dreaming 来组织记忆。这可以纠正错误、创建笔记、构建新的记忆表征，或塑造预先加载进未来 sessions 的内容。

### 记忆笔记（Memory notes）

所谓 “智能体记忆”，我们指的是 Claude 从经验中获得的知识——包括与用户的交互和被分配的任务——并且在 sessions 之间保留，保存为它可以稍后阅读的 context。它不包括模型学习和管理 context 的其他方式，例如对其 *weights*（训练期间设定的内部参数）的更改、[*in-context learning*](https://www.anthropic.com/research/in-context-learning-and-induction-heads)（在单次对话中获得的知识），以及 [*compaction*](https://platform.claude.com/docs/en/build-with-claude/compaction)（由 Claude 撰写的、替换其较旧轮次以便在新的 context window 中继续工作的摘要）。

在人脑中，在体验之前、期间或之后释放的化学信号可以把一段记忆[标记为重要](https://www.nature.com/articles/385533a0)。被标记的记忆在离线期间往往比未标记的记忆被更频繁地重放。这一过程称为 *replay*（重放），有助于稳定它们并把它们整合进长期记忆。

类似地，Claude 可以在 session 日志中把显著事件在发生时打上标签，以便稍后更容易找到，或者可以[把它们写入](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool)一个记忆存储，例如一个记忆笔记文件夹（图 2）。但 Claude 如何能在知道接下来会发生什么之前，在当下判断什么是显著的？

（原文配图：同一记忆层次，记忆笔记层被突出。箭头从 session 直接指向记忆笔记，描述为 Claude 撰写的显著观察。）

Claude 可以向记忆写笔记。

### 记忆可以是对未来将需要什么的预测

记忆偶尔是一种预测。通过写下一条规则，智能体预测它所描述的模式将再次相关。例如，写下一条已经核实的事实，就是预测未来 session 中的智能体将希望依赖该事实而不再次核对。随着时间推移，Claude 在做出这类预测方面已经好得多。

考虑 [Continual Learning Bench（CL-Bench）1.0](https://continual-learning-bench.com/news/cl-bench-1-0/) 中的一项任务，该基准衡量智能体为处理长周期任务而使用记忆的能力。其中一项特定任务要求 Claude 通过在数据库中查找信息来回答一系列问题。在 Claude 给出答案后，它被告知正确解，并可以写一条记忆来帮助回答未来问题。

记忆可以在这里支持一个学习循环。如果 Claude 答错了问题，它可以记录失败、提出关于哪里出错的理论、测试这些理论，并把发现转化为关于未来如何作答的规则。

我们使用 [Claude Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview) 运行了 CL-Bench 1.0 任务。Claude 在新的 session 中开始每个问题，只有一个例外：它可以从一个跨 session 持久化的[记忆目录](https://platform.claude.com/docs/en/managed-agents/memory)中检索文件。

不同模型在创建自己的学习循环方面达到了不同的成功程度。Claude Sonnet 4.6 做到了生成关于为何答案错误的理论。它的记忆目录包含零散文件，每份都列出若干未经测试的猜测。

（原文配图：左：CL-Bench 数据库任务上的平均奖励柱状图，无状态基线 vs. 记忆存储。Opus 5.5：0.655、0.838。Sonnet 5.5：0.644、0.833。Opus 5：0.564、0.828。Opus 4.7：0.383、0.700。Sonnet 5：0.306、0.610。Sonnet 4.6：0.330、0.364。右：相同模型在有无记忆情况下，30 个问题上的滚动平均奖励折线图。）

CL-Bench 数据库任务，跨模型比较记忆与无状态基线。

Claude Opus 4.7 把它的笔记合并成一份单一参考文档，并开始标记哪些事实已经检查、哪些仍未确认。Claude Sonnet 5 在评分器检查之后把每个答案标记为已确认，并在答错时写下一份更正。

Claude Opus 5 是这些模型中第一个闭合循环的。它的大多数条目都包括一条规则（以及它如何知道该规则为真）、对先前问题的答案，以及关于沿途发现的陷阱的清晰警告（图 3）。

与 Opus 5 一样，Claude Opus 5.5 和 Claude Sonnet 5.5 都闭合了循环，使用记忆捕获关于如何最好地回答未来问题的已验证规则。有了记忆，两者的分数与 Opus 5 大致相同，尽管它们在没有记忆时的基线表现略高。

### Claude 已经学会判断显著性

我们还评估了 Claude 玩 *Pokémon Red* 的能力，这是一款[挑战 Claude 导航](https://www.youtube.com/watch?v=CXhYDOvgpuU)复杂长周期任务的游戏，作为对 Claude 关于把*什么*保存到记忆中的判断力的测试。在每次运行开始时，我们给每个模型一个记忆文件文件夹，它可以在游戏过程中从中读取和向其中写入（图 4）。

我们比较了 Claude Sonnet 3.7 和 Claude Fable 5 各自一次运行的记忆文件夹，当时每个模型大约进行了 10,000 步。我们注意到的一个关键差异是，每个模型认为什么值得记住。Sonnet 3.7 假定一切都可能重要，并无差别地向记忆写入。它的记忆文件夹包含一份遭遇档案，常常为它打过的每一场战斗、找到的每一件物品、遇见的每一个非玩家角色都单独设立文件。最终，Sonnet 3.7 在 225 个文件夹中写了 413 个记忆文件，并赢得一枚徽章（徽章标记玩家在游戏中的进度）。

相比之下，Fable 5 在两个文件夹中写了九个文件，外加一个名为 `global.md` 的顶层文件，并赢得四枚徽章。

（原文配图：同一比例下两个 Pokémon 记忆目录的树状图，面积表示记忆字符数。Claude Sonnet 3.7 的很大很拥挤，有 413 个文件和 977,930 个字符，分布在 locations、main、battles 以及若干 “consolidated” 文件夹中。Claude Fable 5 的很小，有 10 个文件和 43,406 个字符，分布在 locations、gameplay 和 global.md 中。）

Claude 在玩 Pokémon 时，Sonnet 3.7 与 Fable 5 的记忆目录。

Sonnet 3.7 的方法之所以成为问题，主要是因为 Pokémon 的游戏状态不断变化——Sonnet 3.7 的详细记录在持续过时。结果是，随着 Claude 进展，它必须花更多时间和资源梳理记忆，而不是玩游戏。例如在大约第 10,000 步，Sonnet 3.7 开始了它的第四个 “master” 记忆文件文件夹。在接下来的 17 步中，它创建了六个文件，删除了另外九个，并且没有在游戏本身中采取任何动作。

Fable 5 的方法把记忆用于游戏没有明确告诉它的事情。Sonnet 3.7 写入记忆的某些信息种类——例如玩家有多少钱，或玩家在地图上的位置——每一回合都可以从屏幕上读出，因此存储它是冗余的。相比之下，关于策略、计划和已测试规则的记忆文件，只有在 Claude 把它们想出来时才存在，除非 Claude 把它们写下来，否则就会消失。

Fable 5 相应地组织了它的记忆。它的 `global.md` 文件充当仪表盘，保存当前目标、一份预先写好的应对道馆（赢得徽章的挑战）的计划，以及模型自己关于如何使用记忆的规则。一个 `locations` 文件夹保存导航特定路线的计划，一个 `gameplay` 文件夹保存基于它对游戏工作方式所学到的策略。例如，在连续七个精灵球未能捕捉一只 Magikarp（最容易捕捉的 Pokémon 之一）之后，Claude 写道：“If 3+ balls fail in a row, VARY the timing (insert extra ‘wait’ presses between menu steps) - the catch landed right after doing this.”

凭借小得多的记忆文件夹，Fable 5 在游戏中比 Sonnet 3.7 进展得远得多。Opus 5.5 采取了类似方法：它保持一个跟踪当前目标和下一步的小型记忆笔记文件夹，在游戏过程中重写它们，并通关了游戏。

### 引导 Claude 写记忆

我们发现，告诉 Claude 记忆是为了什么会有帮助，但不要告诉它*如何*使用记忆。在 CL-Bench 上，我们只是告诉 Claude 有一个记忆文件夹可用。这一一般指导就足以让 Opus 4.7 和 Opus 5 有效使用记忆，并且给两者带来了显著的表现提升（图 3）。

我们还测试了给模型关于它们应当向记忆写什么的具体规则，每次测试一条规则。我们比较了每个模型在有该规则时从记忆中获得多少，与没有该规则时获得多少。当我们把规则设为 “只记录失败” 时，Opus 5 和 Opus 4.7 都失去了记忆给它们带来的大部分表现提升（图 5，右）。对于更强的模型，给它们判断显著性的自由，比预先设定固定规则更有效，而这些规则最终可能削弱表现。

（原文配图：左：Sonnet 4.6 在 CL-Bench 数据库任务上的平均奖励柱状图：基线 0.330，有记忆 0.364，有记忆且精炼指令 0.641。参考线标记有记忆的 Opus 4.7 为 0.700、有记忆的 Opus 5 为 0.828。右：被告知只记录失败时记忆收益的变化：Opus 5，−0.234；Opus 4.7，−0.150；Sonnet 4.6，−0.020。）

左：Sonnet 4.6 在有无引导记忆使用的 prompting 情况下，在 CL-Bench 数据库任务上的表现。右：当被告知只记录失败时，每个模型从记忆中获得的收益变化了多少。

我们还注意到，引导对较老模型帮助最大。例如，Sonnet 4.6 常常不从记忆目录中阅读文件，并且未能测试它关于为何答案错误的理论。

在这种情形中，提示 Claude 在作答前阅读其记忆文件——然后显式测试其理论——几乎把它的基准分数翻倍（图 5，左）。Sonnet 5 会自己这样做。在没有被提示的情况下，它在 10 次中有 9 次在作答前阅读记忆。相比之下，Sonnet 4.6 这样做的次数不到一半。

对于前沿 Claude 模型，我们通常给出简单指导：在有人要求它们时，或当某件事显然值得记住时创建记忆笔记，并把这一判断留给 Claude。

### Dreaming 可以纠正记忆

因为 Claude 根据它在 session 中判断为显著的内容向记忆写入，一条从一开始就错误的笔记，或随着环境变化而漂移的笔记，可能被后来 session 中的 Claude 阅读并信任。

Dreaming 给 Claude 一种对照原始 transcripts 测试其笔记的方式（图 6）。我们在 Claude 使用带有挂载记忆目录的 Managed Agents 玩 Pokémon 时，看到了这一点的正面例子。

（原文配图：带 dreaming 的记忆层次，突出从 transcripts 层向上指向记忆笔记层的箭头，显示 dreaming 对照 transcripts 纠正笔记。）

Dreaming 可以纠正记忆中的错误。

在游戏的一部分中，玩家必须穿过 Mt. Moon，这是一个入口在地图西侧、出口在东侧的洞穴系统。入口附近有一个陷阱：一个单向岩架，会把玩家掉落到他们来时的路线上，没有明显的方法再爬上去。Claude 把位于山入口处的一栋建筑 PokéCenter 用作地标，因此它是否走下岩架，取决于它认为 PokéCenter 在山的哪一侧。

有一次，Claude（错误地）写下 PokéCenter 在东侧。当它走出 PokéCenter 时，它宣布：“Mt Moon is behind me，”并更新了笔记：“Mt Moon DONE。”但 Mt. Moon 并不在它身后。几个动作之后，Claude 越过岩架，落回了它来时的路线（图 7）。它的导航工具没有显示这次下落，因此 Claude 得出结论：“I overshot far west，”并且它一直都在正确的一侧。其实并不是。

（原文配图：两张 Pokémon 地图面板，智能体在岩架旁边。左，“Raw memory”，存储的笔记是错的：箭头显示智能体朝下一座城市前进。右，“Memory + dreaming”，一次离线过程纠正了笔记：箭头显示智能体返回洞穴入口。）

一条被纠正的记忆笔记改变了 Pokémon 中的结果。使用未纠正的笔记时，Claude 说 “Mt Moon is behind me”，朝下一座城市前进，最终回到了来时的路线。使用被 dreaming 纠正的笔记时，它说 “Now I need to find the Mt Moon cave entrance to re-enter”，并返回洞穴。

我们随后测试 dreaming 是否能帮助 Claude 避开这一陷阱。我们在包含错误 PokéCenter 位置的记忆文件夹上运行了 dreaming：Claude 对照 session transcript 检查了该笔记，抓住了错误，并重写了它。Transcript 给了 Claude 一个对照记忆进行验证的 ground truth。有了被纠正的记忆笔记，Claude 直接返回 Mt. Moon，并最终到达 Cerulean City。

在使用未纠正笔记的运行中，Claude 三次掉回那条较早的路线。第三次失败后，Claude 似乎放弃了，写道：“I’m going to stop rather than keep looping。”我们设置的自动回复指示它继续。于是它继续了，一路回到山前的小镇 Pewter City，希望在那里治疗和补给。这次运行在 Claude 从未到达 Cerulean City 的情况下结束。

（原文配图：在 3,000 个累积动作上朝 Cerulean 进展的折线图。记忆加 dreaming 的运行在动作 1,935 到达 Cerulean。原始记忆运行掉下岩架并回溯到 Pewter。没有记忆的运行从未到达 Cerulean。）

Dreaming 纠正了记忆，Claude 返回洞穴并到达下一座城市。使用未纠正笔记（“Raw memory”）的运行从未越过这座山，没有记忆的运行也没有。

### Dreaming 可以构建新的记忆表征

有了 dreaming，Claude 可以构建帮助导航记忆的表征（图 9）。它使用的一种记忆表征称为 [*wiki*](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)，是由 Claude 撰写和维护的一组页面，汇集 Claude 关于某一主题所知道的内容，并把它链接到其他笔记。这些链接实际上为 Claude 提供了一张地图，它可以用来筛选记忆，并在需要时高效定位记忆。

（原文配图：带 dreaming 的记忆层次，突出从 transcripts 和记忆笔记向上指向记忆表征层（例如 wikis）的箭头。）

Dreaming 可以构建记忆表征。

像 wikis 这样的表征可以帮助 Claude 遍历其不断增长的知识库。我们使用来自 Stainless（我们在 5 月收购的一家软件公司）的内部文档语料——约 350,000 个文件，大约 420M tokens——探索了 wikis 作为一种记忆表征的好处。我们创建了一套关于该语料的 25 个问题的评估集，并给 Claude 一个搜索工具来探索它。我们还指示 Claude 使用 dreaming 基于这些文件构建一个 wiki。在 128 个 sessions 中，我们提示 Opus 5 智能体探索文件、撰写或纠正带链接的 wiki 页面、合并重复项，并对照来源检查主张。

每个 session 都建立在先前 sessions 中智能体取得的进展之上，使用共享日志来协调工作。当我们把 dreaming 从两个 sessions 扩展到 128 个时，在 25 个问题上的表现从评分标准的 13% 增长到 48%（图 10）。

Claude 增量地构建其 wikis。在创建初始 wiki 之后，它使用后续轮次的 dreaming 来添加、编辑或修剪它。在早期的 dreaming 轮次中，Claude 的知识就像一名新员工，仅基于 wiki 回答问题的能力有限。它做梦越多，其知识地图就越丰富，就像一名资深员工。在我们的测试中，我们发现当同时给 Claude 访问搜索工具时，wiki 对它帮助最大。当它同时使用搜索和 wiki 时，随着该 wiki 增长，Claude 的综合分数从 54% 升到 61%，而仅有搜索工具时为 53%。当 Claude 只用 wiki 回答问题时，其最佳分数为 48%。同时使用搜索和 wiki 还为每个问题节约了大约 20,000 tokens。

（原文配图：中：随着 wiki 生成从 2M 增长到 128M dreaming tokens，达到的评分标准折线图。Wiki 加搜索工具从 54% 升到 61%，仅 wiki 从 13% 升到 48%，没有 wiki 的搜索工具平坦地保持在 53%。左和右：示例 wiki 的网络图，两次 sessions 后有 103 页和 766 条链接，128 次 sessions 后有 222 页和 12,893 条链接。）

中：Claude 在连续 sessions 中构建 wikis 时，关于一家公司文档语料的 25 个问题上的分数。左和右：两次和 128 次 sessions 后的示例 wiki；每个点是一页，线连接被链接的页面。

我们想测试哪些种类的任务会从 Claude 拥有 wiki 中受益。为此，我们使用了 [Harvey LAB](https://github.com/harveyai/harvey-labs) 基准以及一套关于一次并购的文档集合。该基准给 Claude 一套文档，并要求 Claude 基于其内容生成一份法律简报。然后基准对照一份标准列表为该简报打分。虽然也许不如一次 Pokémon 运行那么吸引人，但这些评估给我们提供了用于构建 wikis 的多样文档集合。

我们指示 Claude 从文档构建一个 wiki。然后我们请 Claude 既从 wiki 也从直接文件搜索来回答问题（关于并购）或生成法律简报（LAB 基准）。一项测试问了 24 个关于并购的问题（图 11，左），其中一半以上需要 Claude 跨若干文档寻找信息，许多还需要 Claude 运用判断或做数学。在那些项目上（红色和橙色线），Claude 在查阅 wiki 时得到 87%，而仅使用搜索时为 73%。

（原文配图：两张把评分标准链接到来源文档的图。左，wiki 显示出更多收益的任务：24 条标准中的大多数连接到 10 份文档中的两份或更多，九条需要判断或算术。右，wiki 显示出较少收益的任务：57 条标准中的大多数可以通过文本搜索在单份文档中找到，通常是交易概述备忘录。）

每个面板列出被评分的内容（左）以及满足每一项所需的来源文档（右）。左：关于一次并购的 24 个问题，大多可以通过查看公开申报文件来回答。一半以上的标准需要组合来自若干文档的信息。右：一项 wiki 没有显示明确收益的 LAB 任务。大多数标准可以从单份文档满足。

在其他情形中，wiki 用处较小。在一项 LAB 任务中（图 11，右），简报标准常常可以通过对单份文档的文本搜索检索到，wiki 相对搜索没有显示明确的表现收益。在另一项 LAB 任务中，wiki 变得比文档本身更大（图 12）。就像 Borges 那篇只有一段的短篇《科学的精确性》（“On Exactitude in Science”）中的制图师，他们绘制了一张细致到与它所代表的帝国一样大的地图，Claude 制作了一个极其详细的、实际上没有抽象任何东西的 wiki。

（原文配图：wiki 构建与第二轮的示意图。左边，一个圆圈容纳语料：10 份文档，115 KB 文本。箭头指向一个更大的圆圈，容纳由此构建的 wiki：68 页、255 条链接和 203 KB，是语料的 1.77 倍。wiki 的一些页面没有链接。）

wiki 变得比原始文件更大。

### Dreaming 可以把笔记提升到记忆层次的上方

Dreaming 也可以把笔记浮到记忆层次的顶部，智能体 harness 可以在每个 session 开始时预先把它们加载进 Claude 的 context（图 13）。这意味着 Claude 不需要搜索它们，甚至不需要知道有什么要搜索。

把记忆提升到新 session 中（一种 *context injection*）必须谨慎进行。被注入的记忆会消耗宝贵的 tokens，一条不正确的笔记可能被带进每一个 session。加载一条笔记也不能保证 Claude 会按它行动：我们关于 [Claude Code](https://code.claude.com/docs/en/memory) 的文档警告，更长的指令文件会降低遵守程度。因此记忆层次的顶层必须保持相对较小，而 dreaming 在这里的大量工作就是保持它那样——把一些细节下移到层次下方，并留下链接。

[Claude Code 的 auto memory](https://code.claude.com/docs/en/memory) 以同样的方式保持其注入层很小，由 Claude 在 session 期间维护它。Claude 不会把它的全部 auto memory 加载进每个 session 的 context window。它只加载 `MEMORY.md` 的前 200 行或 25 KB。这个页眉充当索引，向 Claude 展示它所知道的内容以及在哪里找到它。

（原文配图：带 dreaming 的记忆层次，突出从 transcripts 和记忆表征向上指向顶部注入 context 层的箭头，该层进入下一个 session。）

Dreaming 可以向记忆层次的顶部写入。被注入的 context 被加载进每个 session，其下方的层在 Claude 需要时被阅读或搜索。

### Dreaming 可以把记忆聚焦于特定目标

Dreaming 也可以塑造记忆如何增长。例如像 [Claude Duet](https://support.claude.com/en/articles/17631495-get-started-with-claude-duet) 这样的助手，常常受益于围绕它所帮助的人来组织的记忆，而 dreaming 可以被调优为服务于特定目标来构建记忆。

引导记忆如何增长的指令因任务而异，并告诉 Claude 哪些信息真正重要。例如，LAB 基准中的一项任务模拟一次公司收购，并提供一套合同。简报根据它是否正确描述合同条款被评分。

我们从生成 wiki 的基本指令开始，这些指令没有告诉 Claude *如何*使用 wiki。这项任务严重依赖合同条款。在 wiki 被构建时，若干智能体同时向一张共享的合同条款表写入（图 14，左）。

（原文配图：两张图。之前：四个智能体向同一共享页面 provisions.md 写入，一个智能体的保存擦除了另一个的行；57 条被评分事实中有 41 条幸存。之后：四个智能体各自撰写自己合同的页面，条款逐字复制；57 条中的 57 条都幸存。）

在指令改变前后，有多少被评分的合同事实进入了 wiki。左：若干智能体向一个共享页面写入；57 条事实中有 41 条幸存。右：每个合同一个智能体，各自撰写自己的页面并逐字引用条款；57 条中的 57 条都幸存。

结果是一个缺失关键事实的 wiki。当我们为从该 wiki 生成的简报打分时，Claude 只包含了 57 条事实中的 41 条（72%）。当我们查看哪里出错时，发现共享表对合同条款的摘要很差，并且完全缺失了其中一些，因为智能体互相覆盖了彼此的工作。

合同条款是 wiki 中最重要的部分，但指令并没有这样说。为了找到更好的指令，我们运行了一个循环：Claude 反思其失败，提出对指令的改动，并重建 wiki。这个循环使 Claude 发现遵循合同条款有多么重要，并相应地重写了构建 wiki 的指令。

每份合同在 wiki 中都有自己的页面，由单个智能体撰写，逐字引用条款，而不是把它们摘要进一张共享表。当我们为从这个改进后的 wiki 生成的简报打分时，100% 的标准都能被满足，从 72% 提升上来。

### Dreaming 可以填补 session 留下的缺口

当 Claude 撰写记忆笔记时，它只看到*那个*特定 session 中的 context。Dreaming 可以跨许多 sessions 搜索，以找到共同模式或纠正常见错误。

在为 LAB 基准构建 wikis 时（例如见图 14），有时 Claude 会链接到尚未被创建的页面。第二轮 dreaming 关闭了许多这类缺口。在一项任务中（图 15），dreaming 在 wiki 中找到了指向一个缺失页面的九条链接，并把它们重新指向同一文档的一个已有页面。它还添加了三个新页面，包括一个索引，以改进 wiki。

（原文配图：一张 wiki 的两张网络图。第二轮之前：38 个条目和 225 条链接，来自六个页面的九条链接指向不存在的 “escrow-agreement”。之后：41 个条目和 278 条链接，全部九条链接指向 “buyer-form-escrow-agreement”，并有三个新页面：index、instructions email 和 escalations。）

第二轮 dreaming 之前和之后的 wiki。

### 向后思考，向前望去

关于如何为智能体设计记忆系统，仍有许多开放问题。其中一个是 Claude 应当何时创建记忆。当 Claude 处理一项任务时，它可以向记忆存储（例如文件夹、文件或数据库）写入，在源头捕获显著性，并使重要细节立即可用于未来的轮次或 sessions。但在当下记录笔记，不可避免地会把 Claude 的注意力从其主要任务上拉开。相比之下，dreaming 可以把记忆创建推到后台，但 dreaming 的任何输出可能不会立即对 Claude 可用。

另一个问题是如何可靠地保持记忆是最新的。Claude 可能做出不正确的预测，或向记忆写下从一开始就错误的规则。记忆也可能随着环境变化而漂移并变得无关。Dreaming 是修复这些错误的一种方式（图 8），但它需要计算。指示 Claude 持续检查*全部*记忆可能并不实际。也许重要的是把 dreaming 聚焦于可能变化的信息，或仔细调优 dreaming 的节奏（例如基于记忆被访问的频率）。

把 transcript 搜索视为 Claude 记忆的基础，也是合理的。把表征（例如 wikis）与搜索组合（图 10）有时可能有效。但 Claude 需要使用计算来维护记忆表征，并确保它们不会累积错误或幻觉。

尽管 Claude 关于显著性的判断已经改进，没有任何模型能真正知道未来轮次会发生什么。Dreaming 给 Claude 一个*向后*看的机会，并使用计算来组织其记忆、纠正错误，以及维护使未来 sessions 能更方便地访问记忆的表征。随着 Claude 变得更有能力，记忆系统将会演化，关于设计 Claude 的记忆系统，我们仍有很多要学习。

参见我们关于[开始使用 dreaming](https://platform.claude.com/cookbook/managed-agents-cma-dreaming-with-a-dynamic-workflow) 和 [knowledge wikis](https://github.com/anthropics/claude-quickstarts/tree/main/managed-agents/knowledge-wiki) 的 cookbooks。

## 作者与致谢

由 Lance Martin 撰写，Caitlin Love、Tom Chivers、Rebecca Hiscott、Jake Eaton 和 Blake Wilson 提供编辑指导。感谢 Barry Zhang、Theodora Chu、Daliang Li、Mahesh Murag、Jake Noble、Ravi Trivedi、Tina Vachovsky、Brad Abrams、Henry de Valence、Jeremy Fox、Matt Bell、Allen Li、Chris Gorgolewski、Eugene Yan、Artur Renault、Wei Zhang 和 Kevin Chen 的有益讨论和贡献，以及 David Hershey 的 Claude Plays Pokémon。图表由 Monika Tuchowska 制作。
