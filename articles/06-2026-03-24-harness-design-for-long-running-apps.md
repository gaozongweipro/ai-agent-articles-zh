# 面向长时运行应用开发的 Harness 设计

- 英文标题：Harness design for long-running application development
- 中文标题：面向长时运行应用开发的 Harness 设计
- 发布日期：2026-03-24
- 原文链接：https://www.anthropic.com/research/harness-design-long-running-apps
- 翻译类型：全文翻译

---

*由 Prithvi Rajasekaran 撰写，他是我们 [Labs](https://www.anthropic.com/news/introducing-anthropic-labs) 团队的成员。*

在过去几个月里，我一直在处理两个相互关联的问题：让 Claude 产出高质量的前端设计，以及让它在没有人工干预的情况下构建完整应用。这项工作源于我们较早在 [frontend design skill](https://github.com/anthropics/claude-code/blob/main/plugins/frontend-design/skills/frontend-design/SKILL.md) 和 [长时运行编程智能体 harness](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) 上的努力，我和同事们通过 prompt engineering 和 harness 设计，把 Claude 的表现提升到远高于基线——但两者最终都碰到了天花板。

为了突破，我寻找在两个相当不同的领域中都能成立的新颖 AI 工程方法：一个由主观品味定义，另一个由可验证的正确性和可用性定义。受 [生成对抗网络（Generative Adversarial Networks，GANs）](https://en.wikipedia.org/wiki/Generative_adversarial_network) 启发，我设计了一种带有 **generator（生成器）** 和 **evaluator（评估器）** 智能体的多智能体结构。构建一个能可靠——并且带有品味——为输出打分的评估器，意味着首先要发展一套标准，把“这个设计好吗？”这样的主观判断转化成具体、可评分的条款。

然后我把这些技术应用到长时运行的自主编程上，并沿用了我们较早 harness 工作中的两条教训：把构建分解为可处理的块，以及使用结构化产物在 sessions 之间交接 context。最终结果是一种三智能体架构——planner、generator 和 evaluator——在持续数小时的自主编程 sessions 中产出了丰富的全栈应用。

## 为何朴素实现不够

我们先前已经表明，harness 设计对长时运行智能体式编程的有效性有实质性影响。在较早的一次[实验](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)中，我们使用一个 initializer 智能体把产品规格分解成任务列表，以及一个一次实现一个功能的编程智能体，然后交接产物以跨 sessions 携带 context。更广泛的开发者社区已经收敛到类似洞见，例如 “[Ralph Wiggum](https://ghuntley.com/ralph/)” 方法使用 hooks 或脚本让智能体保持在持续迭代循环中。

但仍有一些问题持续存在。对于更复杂的任务，智能体仍倾向于随时间脱轨。在分解这一问题时，我们观察到智能体在执行这类任务时有两种常见失败模式。

第一是随着 context window 被填满，模型往往在冗长任务上失去连贯性（见我们关于 [context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) 的文章）。有些模型还会表现出 “context anxiety”，即它们在接近自己认为的 context 上限时开始过早收尾。Context resets——完全清空 context window 并启动一个全新智能体，结合一份携带先前智能体状态和下一步的结构化交接——同时应对这两个问题。

这不同于 compaction，后者是把对话较早部分就地摘要，使同一个智能体可以在缩短后的历史上继续。虽然 compaction 保留了连续性，但它并不给智能体一块干净的石板，这意味着 context anxiety 仍可能持续。Reset 提供一块干净的石板，代价是交接产物必须有足够状态，使下一个智能体能干净地接手工作。在我们较早的测试中，我们发现 Claude Sonnet 4.5 表现出的 context anxiety 强烈到仅靠 compaction 不足以实现强的长任务表现，因此 context resets 成为 harness 设计的必要部分。这解决了核心问题，但给每次 harness 运行增加了编排复杂度、token 开销和延迟。

第二个我们先前尚未应对的问题是自我评估。当被要求评估自己产出的工作时，智能体倾向于自信地赞美该工作——即使在人类观察者看来，质量显然只是平庸。这一问题在设计等主观任务上尤其突出，那里没有等价于可验证软件测试的二元检查。布局感觉精致还是一般，是一种判断，而智能体在为自己的工作打分时可靠地偏向正面。

然而，即使在确实有可验证结果的任务上，智能体有时仍会表现出妨碍其完成任务表现的糟糕判断。把做工作的智能体与评判它的智能体分开，被证明是应对这一问题的有力杠杆。这种分离本身并不会立即消除那种宽厚；评估器仍然是一个倾向于对 LLM 生成的输出宽厚的 LLM。但把一个独立评估器调优为怀疑态度，结果远比让生成器对自己的工作保持批判更容易处理，而且一旦那种外部反馈存在，生成器就有了可以迭代对照的具体内容。

## 前端设计：让主观质量变得可评分

我从在前端设计上实验开始，那里自我评估问题最明显。在没有任何干预的情况下，Claude 通常会倾向于安全、可预测的布局，技术上可用，但视觉上平淡无奇。

两点洞见塑造了我为前端设计构建的 harness。第一，虽然审美无法完全还原成一个分数——而且个人品味总会有差异——但可以用编码设计原则和偏好的评分标准来改进它们。“这个设计美吗？”很难一致地回答，但“这是否遵循我们关于好设计的原则？”给了 Claude 可以对照打分的具体内容。第二，通过把前端生成与前端评分分开，我们可以创建一个把生成器推向更强输出的反馈循环。

带着这一点，我写了四条评分标准，并把它们同时交给生成器和评估器智能体的 prompts：

- **设计质量（Design quality）：** 设计感觉像一个连贯的整体，而不是零件的集合吗？这里的出色工作意味着颜色、字体、布局、图像和其他细节结合起来，创造出独特的情绪和身份。
- **原创性（Originality）：** 是否有定制决策的证据，还是模板布局、库默认值和 AI 生成的模式？人类设计师应当能识别出有意的创造性选择。未经修改的库存组件——或紫色渐变覆盖白色卡片等 AI 生成的标志性迹象——在这里会失败。
- **工艺（Craft）：** 技术执行：字体层次、间距一致性、色彩和谐、对比度。这是能力检查而不是创造力检查。大多数合理实现默认在这里表现不错；失败意味着基本功出了问题。
- **功能性（Functionality）：** 独立于审美的可用性。用户能否理解界面做什么、找到主要动作，并在无需猜测的情况下完成任务？

我强调设计质量和原创性，超过工艺和功能性。Claude 默认已经在工艺和功能性上得分很好，因为所需的技术能力往往对模型来说是自然的。但在设计和原创性上，Claude 常常产出最多只能算平淡的输出。这些标准显式惩罚高度一般的 “AI slop” 模式，并且通过更重地加权设计和原创性，把模型推向更多审美上的冒险。

我使用带有详细分数拆解的 few-shot 示例校准评估器。这确保评估器的判断与我的偏好对齐，并减少跨迭代的分数漂移。

我在 [Claude Agent SDK](https://platform.claude.com/docs/en/agent-sdk/overview) 上构建了这个循环，这使编排保持直接。生成器智能体首先基于用户 prompt 创建一份 HTML/CSS/JS 前端。我给评估器 Playwright MCP，使它可以在为每条标准打分并撰写详细评论之前，直接与实时页面交互。在实践中，评估器会自行导航页面，截图并仔细研究实现，然后再产出评估。该反馈作为下一次迭代的输入流回生成器。我每次生成运行 5 到 15 次迭代，每一次迭代通常都会随着生成器回应评估器的评论，把它推向更独特的方向。因为评估器在主动导航页面，而不是为一张静态截图打分，每个循环都花费真实的墙钟时间。完整运行可以长达四小时。我还指示生成器在每次评估后做出战略决策：如果分数趋势良好，则精炼当前方向；如果该方法不起作用，则转向完全不同的审美。

跨多次运行，评估器的评估会随迭代改进，然后趋于平稳，仍有提升空间。有些生成会增量精炼。另一些会在迭代之间出现急剧的审美转向。

标准的措辞以我并未完全预料到的方式引导了生成器。包含诸如 “最好的设计是博物馆品质” 这样的短语，把设计推向一种特定的视觉收敛，表明与标准相关的 prompting 直接塑造了输出的品格。

虽然分数通常会随迭代改进，但这一模式并不总是干净地线性。后来的实现整体上往往更好，但我经常看到自己更喜欢中间某次迭代而不是最后一次的情况。实现复杂度也往往随轮次增加，生成器为回应评估器的反馈而追求更有野心的方案。即使在第一次迭代，输出也明显好于完全没有 prompting 的基线，表明标准和相关语言本身就在任何评估器反馈带来进一步精炼之前，把模型从一般默认值上引开了。

在一个值得注意的例子中，我提示模型为一座荷兰艺术博物馆创建网站。到第九次迭代时，它为一座虚构博物馆产出了一个干净、深色主题的落地页。该页面在视觉上精致，但大体符合我的预期。然后，在第十个循环中，它完全抛弃了这一方法，并把站点重新想象为一种空间体验：一个用 CSS 透视渲染的带格子地板的 3D 房间，艺术品以自由形式的位置挂在墙上，并且用基于门口的导航在画廊房间之间移动，而不是滚动或点击。这是我此前在单次生成中从未见过的那种创造性飞跃。

## 扩展到全栈编程

有了这些发现，我把这种受 GAN 启发的模式应用到全栈开发。生成器-评估器循环自然映射到软件开发生命周期，在那里代码审阅和 QA 扮演与设计评估器相同的结构角色。

### 架构

在我们较早的[长时运行 harness](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) 中，我们已经用 initializer 智能体、一次做一个功能的编程智能体，以及 sessions 之间的 context resets，解决了连贯的多 session 编程。Context resets 是一个关键解锁：该 harness 使用 Sonnet 4.5，它表现出前面提到的 “context anxiety” 倾向。创建一套在 context resets 之间仍能良好工作的 harness，是让模型保持在任务上的关键。Opus 4.5 很大程度上自己消除了那种行为，因此我能够从这套 harness 中完全去掉 context resets。智能体在整个构建中作为一次连续 session 运行，由 [Claude Agent SDK](https://platform.claude.com/docs/en/agent-sdk/overview) 的自动 compaction 沿途处理 context 增长。

对于这项工作，我在原始 harness 的基础上构建了一套三智能体系统，每个智能体应对我在先前运行中观察到的一个特定缺口。系统包含以下智能体角色：

**Planner（规划器）：** 我们先前的长时运行 harness 要求用户预先提供详细规格。我想自动化这一步，因此创建了一个规划器智能体，它接收一个简单的 1–4 句 prompt，并把它扩展成完整的产品规格。我提示它在范围上要有野心，并聚焦于产品 context 和高层技术设计，而不是详细的技术实现。这种强调是因为担心：如果规划器试图预先指定细粒度技术细节并且弄错了什么，规格中的错误就会级联进下游实现。看起来更聪明的做法是在要交付的产物上约束智能体，并让它们在工作过程中自己找出路径。我还请规划器寻找把 AI 功能编织进产品规格的机会。（见文末附录中的示例。）

**Generator（生成器）：** 较早 harness 中一次一个功能的方法在范围管理上效果很好。我在这里应用了类似模型，指示生成器以 sprint 方式工作，每次从规格中拾取一个功能。每个 sprint 用 React、Vite、FastAPI 和 SQLite（后来是 PostgreSQL）技术栈实现应用，并指示生成器在每个 sprint 结束时自我评估其工作，然后再交给 QA。它也有用于版本控制的 git。

**Evaluator（评估器）：** 较早 harness 产出的应用常常看起来令人印象深刻，但你真正尝试使用它们时仍有真实 bug。为了抓住这些，评估器使用 Playwright MCP，像用户一样点击运行中的应用，测试 UI 功能、API 端点和数据库状态。然后它对照所发现的 bug，以及一套以前端实验为模型、在此改编以覆盖产品深度、功能性、视觉设计和代码质量的标准，为每个 sprint 打分。每条标准都有硬阈值，如果任何一条低于它，该 sprint 就失败，生成器会得到关于哪里出错的详细反馈。

在每个 sprint 之前，生成器和评估器会协商一份 sprint 合同：在写任何代码之前，就那一块工作的 “完成” 看起来像什么达成一致。这之所以存在，是因为产品规格有意保持高层，而我想要一步来弥合用户故事与可测试实现之间的鸿沟。生成器提出它将构建什么以及如何验证成功，评估器审阅该提案以确保生成器在构建正确的东西。两者迭代直到达成一致。

沟通通过文件处理：一个智能体写一份文件，另一个智能体阅读它，并在该文件内或用一份先前智能体随后会阅读的新文件回应。生成器随后对照商定的合同进行构建，再把工作交给 QA。这使工作忠实于规格，而不会过早过度指定实现。

### 运行该 Harness

对于这套 harness 的第一个版本，我使用 Claude Opus 4.5，把用户 prompts 同时在完整 harness 和单智能体系统上运行以作比较。我使用 Opus 4.5，是因为这是我开始这些实验时我们最好的编程模型。

我写了下面的 prompt 来生成一个复古电子游戏制作器：

> *Create a 2D retro game maker with features including a level editor, sprite editor, entity behaviors, and a playable test mode.*

下表显示 harness 类型、运行时长和总成本。

| **Harness** | **时长** | **成本** |
| --- | --- | --- |
| Solo | 20 分钟 | $9 |
| Full harness | 6 小时 | $200 |

该 harness 贵了 20 倍以上，但输出质量的差异立即显而易见。

我期待的是一个界面，我可以在其中构建关卡及其组成部件（sprites、实体、图块布局），然后按播放来真正玩该关卡。我先打开 solo 运行的输出，初始应用似乎符合这些预期。

然而，当我点击进去时，问题开始出现。布局浪费空间，固定高度的面板使视口的大部分是空的。工作流很僵硬。试图填充一个关卡会提示我先创建 sprites 和实体，但 UI 中没有任何东西引导我走向那一顺序。更重要的是，实际游戏是坏的。我的实体出现在屏幕上，但没有任何东西对输入作出响应。深入代码发现，实体定义与游戏运行时之间的接线是坏的，表面上没有任何指示说明问题在哪里。

（原文配图：打开由 solo harness 创建的应用时的初始屏幕；在 solo harness 制作的 sprite 编辑器中创建 sprite；试图玩我所创建的关卡但没有成功。）

在评估完 solo 运行后，我把注意力转向 harness 运行。这次运行从同一句 prompt 开始，但规划步骤把该 prompt 扩展成一份分布在十个 sprints 中的 16 项功能规格。它远远超出了 solo 运行所尝试的范围。除了核心编辑器和播放模式之外，规格还要求 sprite 动画系统、行为模板、音效和音乐、AI 辅助的 sprite 生成器和关卡设计器，以及带可分享链接的游戏导出。我给规划器访问我们的 [frontend design skill](https://github.com/anthropics/claude-code/blob/main/plugins/frontend-design/skills/frontend-design/SKILL.md) 的权限，它阅读并使用该 skill 作为规格的一部分为应用创建视觉设计语言。对每个 sprint，生成器和评估器协商一份合同，定义该 sprint 的具体实现细节，以及将用于验证完成的可测试行为。

该应用立即显示出比 solo 运行更多的打磨和流畅。画布使用了完整视口，面板大小合理，界面有与规格中的设计方向一致的视觉身份。我在 solo 运行中看到的一些笨拙仍然存在——工作流仍然没有表明你应当在试图填充关卡之前先构建 sprites 和实体，我必须通过四处探索才搞明白。这被解读为基础模型产品直觉上的缺口，而不是 harness 被设计来应对的东西，尽管它确实暗示了 harness 内部有针对性的迭代可以进一步改进输出质量的地方。

在编辑器中工作时，新运行相对 solo 的优势变得更明显。Sprite 编辑器更丰富、功能更完整，工具调色板更干净，颜色选择器更好，缩放控制更可用。

因为我请规划器把 AI 功能编织进其规格，该应用还带有内置的 Claude 集成，让我可以通过 prompting 生成游戏的不同部分。这显著加快了工作流。

（原文配图：在用完整 harness 构建的应用中创建新游戏的初始屏幕；感觉更干净、更易用的 sprite 编辑器；使用内置 AI 功能生成关卡；玩我所生成的游戏。）

最大的差异在播放模式。我实际上能够移动我的实体并玩游戏。物理有一些粗糙边缘——我的角色跳上一个平台，却最终与它重叠，这在直觉上感觉不对——但核心的事情是有效的，而这是 solo 运行未能做到的。四处移动一阵之后，我确实碰到了 AI 关卡构建的一些限制。有一堵我无法跳过的大墙，因此我被卡住了。这表明还有一些常识性改进和边界情况，harness 可以处理以进一步精炼应用。

阅读日志可以清楚地看到，评估器使实现与规格保持一致。每个 sprint，它都会走一遍 sprint 合同的测试标准，并通过 Playwright 操作运行中的应用，对任何偏离期望行为的东西提交 bug。合同是细粒度的——仅 Sprint 3 就有覆盖关卡编辑器的 27 条标准——评估器的发现具体到无需额外调查就可以采取行动。下表展示了我们的评估器识别出的若干问题示例：

| **合同标准** | **评估器发现** |
| --- | --- |
| Rectangle fill tool allows click-drag to fill a rectangular area with selected tile | **FAIL** — Tool only places tiles at drag start/end points instead of filling the region. `fillRectangle` function exists but isn't triggered properly on mouseUp. |
| User can select and delete placed entity spawn points | **FAIL** — Delete key handler at `LevelEditor.tsx:892` requires both `selection` and `selectedEntityId `to be set, but clicking an entity only sets `selectedEntityId`. Condition should be `selection || (selectedEntityId && activeLayer === 'entity')`. |
| User can reorder animation frames via API | **FAIL** — `PUT /frames/reorder` route defined after `/{frame_id}` routes. FastAPI matches 'r`eorder`' as a frame_id integer and returns 422: "unable to parse string as an integer." |

让评估器达到这一水平花了功夫。开箱即用时，Claude 是一个糟糕的 QA 智能体。在早期运行中，我看着它识别出正当问题，然后说服自己它们不是什么大事，并批准了该工作。它也倾向于做表面测试，而不是探测边界情况，因此更微妙的 bug 常常溜走。调优循环是阅读评估器的日志，找到其判断与我的判断分歧的例子，并更新 QA 的 prompt 来解决那些问题。经过几轮这样的开发循环，评估器的打分方式才让我觉得合理。即便如此，harness 输出仍显示出模型 QA 能力的限制：小的布局问题、在某些地方感觉不直观的交互，以及评估器没有彻底操练的、嵌套更深的功能中未被发现的 bug。显然还有更多验证空间可以通过进一步调优来捕捉。但与 solo 运行相比——那里应用的核心功能根本不工作——提升是显而易见的。

### 迭代该 Harness

第一套 harness 结果令人鼓舞，但它也很臃肿、缓慢且昂贵。合乎逻辑的下一步是找到在不降低表现的情况下简化 harness 的方法。这既是常识，也是一条更一般原则的体现：harness 中的每个组件都编码了一个关于模型独自做不到什么的假设，而这些假设值得做压力测试，既因为它们可能是不正确的，也因为随着模型改进，它们可能很快过时。我们的博文 [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) 把底层思想表述为 “找到尽可能简单的方案，只在需要时增加复杂度”，这是任何维护智能体 harness 的人都会一致看到的模式。

在我第一次简化尝试中，我把 harness 大幅削减，并尝试了一些有创造性的新想法，但我未能复制原始版本的表现。要分辨 harness 设计中哪些部分真正承重、以及以何种方式承重，也变得困难。基于那次经验，我转向更有方法的做法：一次移除一个组件，并审阅它对最终结果的影响。

在我进行这些迭代循环时，我们也发布了 Opus 4.6，这为减少 harness 复杂度提供了进一步动机。有充分理由预期 4.6 会比 4.5 需要更少的脚手架。来自我们的[发布博文](https://www.anthropic.com/news/claude-opus-4-6)：“[Opus 4.6] 规划更仔细，能更长时间地维持智能体式任务，能在更大代码库中更可靠地运作，并有更好的代码审阅和调试技能来抓住自己的错误。”它还在长 context 检索上有实质性改进。这些都是该 harness 被构建来补充的能力。

### 移除 sprint 构造

我首先完全移除了 sprint 构造。Sprint 结构帮助把工作分解成模型可以连贯处理的块。鉴于 Opus 4.6 的改进，有充分理由相信模型可以在没有这种分解的情况下原生处理这项工作。

我保留了规划器和评估器，因为两者都继续增加明显价值。没有规划器，生成器会范围不足：给定原始 prompt，它会在事先不为工作做规格的情况下开始构建，最终创建出比规划器所做的功能更少的应用。

在移除 sprint 构造后，我把评估器移到运行结束时的单次通过，而不是按 sprint 打分。因为模型能力强得多，它改变了评估器在某些运行中的承重程度，其用处取决于任务相对于模型独自能可靠完成的事情处于何处。在 4.5 上，那条边界很近：我们的构建处于生成器独自能做好的边缘，评估器在整个构建中抓住了有意义的问题。在 4.6 上，模型的原始能力提升了，因此边界向外移动。过去需要评估器检查才能被连贯实现的任务，现在常常处于生成器独自就能处理好的范围内，对于那条边界之内的任务，评估器变成了不必要的开销。但对于构建中仍处于生成器能力边缘的那些部分，评估器继续给出真实提升。

实践含义是：评估器不是一个固定的是或否决策。当任务超出当前模型独自可靠完成的范围时，它值得付出成本。

除了结构简化之外，我还加入了 prompting，以改进 harness 如何把 AI 功能构建进每个应用，具体是让生成器构建一个能通过工具驱动应用自身功能的真正智能体。这花了真实的迭代，因为相关知识足够新，Claude 的训练数据对它覆盖得很薄。但经过足够调优后，生成器正确地在构建智能体。

### 更新后 Harness 的结果

为了把更新后的 harness 付诸测试，我使用下面的 prompt 来生成一个数字音频工作站（Digital Audio Workstation，DAW），一种用于作曲、录音和混音的音乐制作程序：

> *Build a fully featured DAW in the browser using the Web Audio API.*

这次运行仍然漫长且昂贵，大约 4 小时和 $124 的 token 成本。

大部分时间花在构建器上，它在没有 Opus 4.5 所需要的 sprint 分解的情况下，连贯运行了两个多小时。

| **智能体与阶段** | **时长** | **成本** |
| --- | --- | --- |
| Planner | 4.7 分钟 | $0.46 |
| Build（第 1 轮） | 2 小时 7 分钟 | $71.08 |
| QA（第 1 轮） | 8.8 分钟 | $3.24 |
| Build（第 2 轮） | 1 小时 2 分钟 | $36.89 |
| QA（第 2 轮） | 6.8 分钟 | $3.09 |
| Build（第 3 轮） | 10.9 分钟 | $5.88 |
| QA（第 3 轮） | 9.6 分钟 | $4.06 |
| **V2 Harness 总计** | **3 小时 50 分钟** | **$124.70** |

与先前的 harness 一样，规划器把一行 prompt 扩展成完整规格。从日志中，我可以看到生成器模型在规划应用和智能体设计、把智能体接好线、并在交给 QA 之前测试它方面做得很好。

话虽如此，QA 智能体仍然抓住了真实缺口。在其第一轮反馈中，它指出：

> This is a strong app with excellent design fidelity, solid AI agent, and good backend. The main failure point is Feature Completeness — while the app looks impressive and the AI integration works well, several core DAW features are display-only without interactive depth: clips can't be dragged/moved on the timeline, there are no instrument UI panels (synth knobs, drum pads), and no visual effect editors (EQ curves, compressor meters). These aren't edge cases — they're the core interactions that make a DAW usable, and the spec explicitly calls for them.

在第二轮反馈中，它再次抓住了若干功能性缺口：

> Remaining gaps:
> - Audio recording is still stub-only (button toggles but no mic capture)
> - Clip resize by edge drag and clip split not implemented
> - Effect visualizations are numeric sliders, not graphical (no EQ curve)

生成器在被留给自己处理时，仍可能遗漏细节或把功能做成桩（stub），而 QA 在抓住这些供生成器修复的最后一公里问题方面仍然增加了价值。

基于该 prompt，我期待的是一个程序，我可以在其中创建旋律、和声和鼓点模式，把它们编排成一首歌，并沿途从集成智能体获得帮助。下面的视频展示了结果。

该应用远不是专业的音乐制作程序，智能体的歌曲创作技能显然还有很多工作要做。此外，Claude 实际上听不到，这使得 QA 反馈循环在音乐品味方面不那么有效。

但最终应用拥有一个可用音乐制作程序的全部核心部件：在浏览器中运行的可用编曲视图、混音器和传输控制。除此之外，我能够完全通过 prompting 拼出一段短小的歌曲片段：智能体设定了速度和调性，铺下旋律，构建了鼓轨道，调整了混音器电平，并加入了混响。歌曲创作的核心原语是存在的，智能体可以自主驱动它们，使用工具端到端地创建一份简单作品。你可以说它还不是完全合拍——但它正在接近。

## 下一步是什么

随着模型持续改进，我们可以大致预期它们能够工作更长时间、处理更复杂的任务。在某些情形中，这意味着围绕模型的脚手架会随时间变得不那么重要，开发者可以等待下一个模型，并看到某些问题自行解决。另一方面，模型越好，就越有空间去发展能完成超出模型基线能力的复杂任务的 harnesses。

带着这一点，这项工作中有几条值得带往未来的教训。始终良好的实践是：针对你正在构建的模型做实验，阅读它在现实问题上的 traces，并调优其表现以实现你期望的结果。在处理更复杂的任务时，有时把任务分解并把专门智能体应用到问题的每个方面会有提升空间。当一个新模型落地时，一般良好的实践是重新审视一套 harness，剥离对表现不再承重的部分，并加入新的部分以实现以前可能不可能的更强能力。

从这项工作中，我的信念是：有趣的 harness 组合空间并不会随着模型改进而缩小。相反，它会移动，而 AI 工程师有趣的工作，是持续找到下一种新颖组合。

## 附录

规划器智能体生成的示例计划。

```plaintext
RetroForge - 2D Retro Game Maker

Overview
RetroForge is a web-based creative studio for designing and building 2D retro-style video games. It combines the nostalgic charm of classic 8-bit and 16-bit game aesthetics with modern, intuitive editing tools—enabling anyone from hobbyist creators to indie developers to bring their game ideas to life without writing traditional code.

The platform provides four integrated creative modules: a tile-based Level Editor for designing game worlds, a pixel-art Sprite Editor for crafting visual assets, a visual Entity Behavior system for defining game logic, and an instant Playable Test Mode for real-time gameplay testing. By weaving AI assistance throughout (powered by Claude), RetroForge accelerates the creative process—helping users generate sprites, design levels, and configure behaviors through natural language interaction.

RetroForge targets creators who love retro gaming aesthetics but want modern conveniences. Whether recreating the platformers, RPGs, or action games of their childhood, or inventing entirely new experiences within retro constraints, users can prototype rapidly, iterate visually, and share their creations with others.

Features
1. Project Dashboard & Management
The Project Dashboard is the home base for all creative work in RetroForge. Users need a clear, organized way to manage their game projects—creating new ones, returning to works-in-progress, and understanding what each project contains at a glance.

User Stories: As a user, I want to:

- Create a new game project with a name and description, so that I can begin designing my game
- See all my existing projects displayed as visual cards showing the project name, last modified date, and a thumbnail preview, so that I can quickly find and continue my work
- Open any project to enter the full game editor workspace, so that I can work on my game
- Delete projects I no longer need, with a confirmation dialog to prevent accidents, so that I can keep my workspace organized
- Duplicate an existing project as a starting point for a new game, so that I can reuse my previous work

Project Data Model: Each project contains:

Project metadata (name, description, created/modified timestamps)
Canvas settings (resolution: e.g., 256x224, 320x240, or 160x144)
Tile size configuration (8x8, 16x16, or 32x32 pixels)
Color palette selection 
All associated sprites, tilesets, levels, and entity definitions

...
```

## 作者与致谢

特别感谢 Mike Krieger、Michael Agaby、Justin Young、Jeremy Hadfield、David Hershey、Julius Tarng、Xiaoyi Zhang、Barry Zhang、Orowa Sidker、Michael Tingley、Ibrahim Madha、Martina Long 和 Canyon Robbins 对这项工作的贡献。

也感谢 Jake Eaton、Alyssa Leonard 和 Stef Sequeira 帮助塑造这篇文章。
