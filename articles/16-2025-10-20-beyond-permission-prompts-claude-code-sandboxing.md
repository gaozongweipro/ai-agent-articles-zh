# 超越权限提示：让 Claude Code 更安全、更自主

- 英文标题：Beyond permission prompts: making Claude Code more secure and autonomous
- 中文标题：超越权限提示：让 Claude Code 更安全、更自主
- 发布日期：2025-10-20
- 原文链接：https://www.anthropic.com/research/claude-code-sandboxing
- 翻译类型：全文翻译

---

在 [Claude Code](https://www.claude.com/product/claude-code) 中，Claude 与你一起编写、测试和调试代码，浏览代码库、编辑多个文件，并运行命令来验证工作。给予 Claude 如此多的代码库和文件访问权限会带来风险，尤其是在发生 prompt injection（提示注入）时。

为应对这一问题，我们在 Claude Code 中推出了两项基于 sandboxing（沙箱）构建的新功能，旨在为开发者提供更安全的工作环境，同时让 Claude 能更自主地运行、减少权限提示。在内部使用中，我们发现 sandboxing 可以安全地把权限提示减少 84%。通过预先划定 Claude 可以自由工作的边界，它们同时提升了安全性和自主性。

## 在 Claude Code 上保障用户安全

Claude Code 采用基于权限的模型：默认是只读的，这意味着它在进行修改或运行任何命令之前会请求许可。也有一些例外：我们对 echo 或 cat 等安全命令自动放行，但大多数操作仍需要明确批准。

不断点击 “approve” 会拖慢开发周期，并可能导致 “approval fatigue（批准疲劳）”——用户可能不再仔细查看自己在批准什么，反而使开发更不安全。

为解决这一问题，我们为 Claude Code 推出了 sandboxing。

## Sandboxing：更安全、更自主的方法

Sandboxing 预先划定边界，让 Claude 在边界内更自由地工作，而不必为每个动作请求许可。启用 sandboxing 后，权限提示会大幅减少，安全性也会提高。

我们的 sandboxing 方法建立在操作系统级特性之上，以实现两类边界：

1. **文件系统隔离（Filesystem isolation）**，确保 Claude 只能访问或修改特定目录。这对防止被 prompt injection 的 Claude 修改敏感系统文件尤为重要。
2. **网络隔离（Network isolation）**，确保 Claude 只能连接到已批准的服务器。这可以防止被注入的 Claude 泄露敏感信息或下载恶意软件。

值得注意的是，有效的 sandboxing 需要*同时*具备文件系统隔离和网络隔离。没有网络隔离，被攻陷的智能体可能把 SSH 密钥等敏感文件外传；没有文件系统隔离，被攻陷的智能体可以轻易逃出沙箱并获得网络访问。正是同时使用这两种技术，我们才能为 Claude Code 用户提供更安全、更快捷的智能体体验。

### Claude Code 中的两项新沙箱功能

#### 沙箱化的 bash 工具：无需权限提示即可安全执行 bash

我们推出了[一种新的沙箱运行时](https://docs.claude.com/en/docs/claude-code/sandboxing)，目前以 beta 研究预览的形式提供。你可以精确指定智能体可以访问哪些目录和网络主机，而不必承担启动和管理容器的开销。它可用于沙箱化任意进程、智能体和 MCP 服务器，并以[开源研究预览](https://github.com/anthropic-experimental/sandbox-runtime)的形式提供。

在 Claude Code 中，我们用这一运行时来沙箱化 bash 工具，让 Claude 在你设定的限制内运行命令。在安全沙箱内，Claude 可以更自主地运行，并在无需权限提示的情况下安全执行命令。如果 Claude 试图访问沙箱*之外*的内容，你会立即收到通知，并可以选择是否允许。

我们基于 [Linux bubblewrap](https://github.com/containers/bubblewrap) 和 macOS seatbelt 等操作系统级原语，在 OS 层强制执行这些限制。它们不仅覆盖 Claude Code 的直接交互，也覆盖该命令催生的任何脚本、程序或子进程。如上所述，这一沙箱同时强制执行：

1. **文件系统隔离：** 允许对当前工作目录进行读写，但阻止修改其外的任何文件。
2. **网络隔离：** 只允许通过连接到沙箱外代理服务器的 unix domain socket 访问互联网。该代理服务器对进程可连接的域名实施限制，并在请求新域名时处理用户确认。若你希望进一步提高安全性，我们还支持自定义该代理，对出站流量强制执行任意规则。

这两个组件都可配置：你可以轻松允许或禁止特定文件路径或域名。

Claude Code 的 sandboxing 架构用文件系统和网络控制隔离代码执行：自动允许安全操作，阻止恶意操作，只在需要时请求许可。

Sandboxing 确保即使发生成功的 prompt injection，也会被完全隔离，无法影响用户的整体安全。这样，被攻陷的 Claude Code 无法窃取你的 SSH 密钥，也无法向攻击者的服务器回连。

要开始使用该功能，在 Claude Code 中运行 `/sandbox`，并查看关于我们安全模型的[更多技术细节](https://docs.claude.com/en/docs/claude-code/sandboxing)。

为了让其他团队也更容易构建更安全的智能体，我们已将这一功能[开源](https://github.com/anthropic-experimental/sandbox-runtime)。我们建议其他人考虑在自己的智能体中采用这项技术，以增强其安全态势。

#### Claude Code on the web：在云中安全运行 Claude Code

今天，我们还发布了 [Claude Code on the web](https://docs.claude.com/en/docs/claude-code/claude-code-on-the-web)，让用户可以在云中的隔离沙箱里运行 Claude Code。Claude Code on the web 在隔离沙箱中执行每个会话，使其能以安全的方式充分访问其服务器。我们设计该沙箱的原则是：敏感凭证（例如 git 凭证或签名密钥）从不进入与 Claude Code 共用的沙箱。这样，即使沙箱中运行的代码被攻陷，用户也能免受进一步伤害。

Claude Code on the web 使用自定义代理服务透明地处理所有 git 交互。在沙箱内，git 客户端用自定义的、范围受限的凭证向该服务认证。代理验证该凭证以及 git 交互的内容（例如确保它只推送到已配置的分支），然后在把请求发送到 GitHub 之前附加正确的认证令牌。

Claude Code 的 Git 集成通过安全代理路由命令，验证认证令牌、分支名和仓库目标——既允许安全的版本控制工作流，又防止未经授权的推送。

## 开始使用

我们新的沙箱化 bash 工具和 Claude Code on the web，为使用 Claude 从事工程工作的开发者在安全性和生产力上都带来了显著改进。

要开始使用这些工具：

1. 在 Claude 中运行 `/sandbox`，并查看[我们的文档](https://docs.claude.com/en/docs/claude-code/sandboxing)以了解如何配置该沙箱。
2. 前往 [claude.com/code](http://claude.ai/code) 试用 Claude Code on the web。

或者，如果你在构建自己的智能体，请查看我们[开源的 sandboxing 代码](https://github.com/anthropic-experimental/sandbox-runtime)，并考虑将其集成到你的工作中。我们期待看到你构建的成果。

要了解更多关于 Claude Code on the web 的信息，请参阅我们的[发布博文](https://www.anthropic.com/news/claude-code-on-the-web)。

## 作者与致谢

### 贡献者

文章由 David Dworken 和 Oliver Weller-Davies 撰写，Meaghan Choi、Catherine Wu、Molly Vorwerck、Alex Isken、Kier Bradwell 和 Kevin Garcia 亦有贡献。

### 致谢

文章由 David Dworken 和 Oliver Weller-Davies 撰写，Meaghan Choi、Catherine Wu、Molly Vorwerck、Alex Isken、Kier Bradwell 和 Kevin Garcia 亦有贡献。
