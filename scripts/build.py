#!/usr/bin/env python3
"""Regenerate data/articles.json, README.md, and the docs/ static site from article Markdown."""
from __future__ import annotations

import json
import re
import shutil
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

import markdown
import yaml

ROOT = Path(__file__).resolve().parents[1]
ARTICLES_DIR = ROOT / "articles"
DATA_DIR = ROOT / "data"
DOCS_DIR = ROOT / "docs"
README = ROOT / "README.md"

TZ = timezone(timedelta(hours=8))

COMPANIES = [
    ("anthropic", "Anthropic", "Anthropic"),
    ("openai", "OpenAI", "OpenAI"),
    ("google", "Google / DeepMind", "Google / DeepMind"),
    ("deepseek", "DeepSeek", "DeepSeek"),
    ("microsoft", "Microsoft", "Microsoft"),
    ("mistral", "Mistral", "Mistral"),
    ("alibaba", "Alibaba Qwen", "阿里通义 Qwen"),
    ("moonshot", "Moonshot Kimi", "月之暗面 Kimi"),
    ("zhipu", "Zhipu GLM", "智谱 GLM"),
    ("meta", "Meta", "Meta"),
]
COMPANY_MAP = {k: (en, zh) for k, en, zh in COMPANIES}

CATEGORIES = [
    "入门与方法论",
    "工具与协议",
    "上下文与记忆",
    "编码 Agent",
    "多 Agent",
    "评测",
    "安全与沙箱",
    "模型与发布",
    "框架与 SDK",
]

TYPE_LABEL = {"full": "全文翻译", "summary": "中文摘要"}

MD = markdown.Markdown(
    extensions=["tables", "fenced_code", "sane_lists", "nl2br", "smarty", "toc"],
    output_format="html5",
)


def parse_article(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError(f"Missing YAML front matter: {path}")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"Invalid front matter: {path}")
    meta = yaml.safe_load(parts[1]) or {}
    body = parts[2].strip()
    rel = path.relative_to(ROOT).as_posix()
    company = meta["company"]
    stem = path.stem
    html_rel = f"articles/{company}/{stem}.html"
    excerpt = make_excerpt(body)
    date = meta["date"]
    if hasattr(date, "isoformat"):
        date = date.isoformat()
    updated = meta.get("updated")
    if updated and hasattr(updated, "isoformat"):
        updated = updated.isoformat()
    typ = meta["type"]
    if typ not in ("full", "summary"):
        raise ValueError(f"Bad type {typ} in {path}")
    if company not in COMPANY_MAP:
        raise ValueError(f"Unknown company {company} in {path}")
    if meta["category"] not in CATEGORIES:
        raise ValueError(f"Unknown category {meta['category']} in {path}")
    tags = list(meta.get("tags") or [])
    if not (3 <= len(tags) <= 6):
        raise ValueError(f"Need 3-6 tags in {path}, got {len(tags)}: {tags}")
    return {
        "id": f"{company}/{stem}",
        "filename": path.name,
        "stem": stem,
        "title_en": meta["title_en"],
        "title_zh": meta["title_zh"],
        "company": company,
        "company_en": COMPANY_MAP[company][0],
        "company_zh": COMPANY_MAP[company][1],
        "date": str(date),
        "updated": str(updated) if updated else None,
        "url": meta["url"],
        "type": typ,
        "type_zh": TYPE_LABEL[typ],
        "category": meta["category"],
        "tags": tags,
        "path": rel,
        "html_path": html_rel,
        "excerpt": excerpt,
        "body": body,
    }


def make_excerpt(body: str, limit: int = 220) -> str:
    text = re.sub(r"^# .+\n+", "", body)
    text = re.sub(r"```[\s\S]*?```", " ", text)
    text = re.sub(r"`[^`]+`", " ", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"[#>*_|-]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "…"


def load_articles() -> list[dict]:
    paths = sorted(ARTICLES_DIR.glob("*/*.md"))
    arts = [parse_article(p) for p in paths]
    # Newest first by date; same-day ties stay alphabetical by English title (stable).
    arts.sort(key=lambda a: a["title_en"].lower())
    arts.sort(key=lambda a: a["date"], reverse=True)
    return arts


def write_json(arts: list[dict]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(TZ).strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "title": "AI Agent 开发文章文库（中文整理）",
        "companies": [
            {"id": k, "name_en": en, "name_zh": zh} for k, en, zh in COMPANIES
        ],
        "categories": CATEGORIES,
        "type_labels": TYPE_LABEL,
        "counts": {
            "total": len(arts),
            "full": sum(1 for a in arts if a["type"] == "full"),
            "summary": sum(1 for a in arts if a["type"] == "summary"),
            "by_company": {
                k: sum(1 for a in arts if a["company"] == k) for k, *_ in COMPANIES
            },
        },
        "articles": [
            {k: a[k] for k in a if k != "body"}
            for a in arts
        ],
    }
    (DATA_DIR / "articles.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    docs_data = DOCS_DIR / "data"
    docs_data.mkdir(parents=True, exist_ok=True)
    (docs_data / "articles.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def write_readme(arts: list[dict]) -> None:
    total = len(arts)
    n_full = sum(1 for a in arts if a["type"] == "full")
    n_sum = total - n_full
    dates = [a["date"] for a in arts]
    span = f"{min(dates)} 至 {max(dates)}" if dates else ""
    companies_present = [c for c in COMPANIES if any(a["company"] == c[0] for a in arts)]

    lines = []
    lines.append("# AI Agent 开发文章文库（中文整理）")
    lines.append("")
    lines.append(
        "本仓库整理多家实验室与模型公司**官方博客、文档与研究文章**中，与 AI Agent 开发相关的内容，并附中文全文翻译或摘要，方便中文读者按主题阅读。"
    )
    lines.append("")
    lines.append(
        "收录范围包括：构建智能体、工具 / function calling、MCP 与 A2A 等协议、context engineering 与记忆、智能体评测（evals）、编码 Agent、多 Agent、记忆、Agent SDK / 框架，以及智能体安全与沙箱。只收录官方来源，每篇均对照原页面核实，不编造标题、日期或链接；不收录 LangChain 等第三方框架的文章。"
    )
    lines.append("")
    lines.append(
        f"目前共收录 **{total}** 篇（**{n_full}** 篇全文翻译，**{n_sum}** 篇中文摘要），时间跨度 **{span}**。"
        "优先为各家最核心的工程长文提供全文翻译，其余以 300–600 字左右的中文摘要收录，类型在页眉与目录中标明。"
    )
    lines.append("")
    lines.append("## 如何阅读")
    lines.append("")
    lines.append("- 推荐打开静态首页：[docs/index.html](docs/index.html)。页面按发表时间从新到旧列出全部文章，可用公司、分类、标签筛选，也可按标题与摘要全文搜索；点击卡片进入阅读页，可看到日期、公司、类型徽标、标签与原文链接。")
    lines.append("- 本地预览：在 `docs/` 目录运行 `python3 -m http.server 8000`，然后访问 `http://127.0.0.1:8000/`。站点全部使用相对路径，也可部署到 GitHub Pages 的 `/ai-agent-articles-zh/` 子路径（本仓库当前未启用 Pages）。")
    lines.append("- 单篇 Markdown 位于 [`articles/<company>/`](articles/)，文件名以序号开头，使同一公司目录在 GitHub 上按从新到旧排列。")
    lines.append("- 机器可读目录由 [`scripts/build.py`](scripts/build.py) 从 YAML 页眉生成，写入 [`data/articles.json`](data/articles.json)（构建时同步到 `docs/data/articles.json`），并同时更新本 README 与站点。")
    lines.append("")
    lines.append("## 文章目录（按公司，从新到旧）")
    lines.append("")
    for cid, en, zh in companies_present:
        group = [a for a in arts if a["company"] == cid]
        group.sort(key=lambda a: a["title_en"].lower())
        group.sort(key=lambda a: a["date"], reverse=True)
        label = zh if zh == en else f"{zh}"
        lines.append(f"### {label}")
        lines.append("")
        lines.append("| 日期 | 标题（英） | 中文标题 | 分类 | 标签 | 类型 | 原文 | 译文 |")
        lines.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
        for a in group:
            date_cell = a["date"]
            if a["updated"]:
                date_cell += f"<br>更新：{a['updated']}"
            tags = "、".join(a["tags"])
            src = f"[原文]({a['url']})"
            trans = f"[{a['filename']}]({a['path']})"
            te = a["title_en"].replace("|", "\\|")
            tz = a["title_zh"].replace("|", "\\|")
            lines.append(
                f"| {date_cell} | {te} | {tz} | {a['category']} | {tags} | {a['type_zh']} | {src} | {trans} |"
            )
        lines.append("")

    # tag index
    tag_map: dict[str, list] = defaultdict(list)
    for a in arts:
        for t in a["tags"]:
            tag_map[t].append(a)
    lines.append("## 标签索引")
    lines.append("")
    lines.append("标签词汇尽量统一，便于筛选。点击首页标签芯片也可过滤。")
    lines.append("")
    for tag in sorted(tag_map, key=lambda x: (-len(tag_map[x]), x.lower())):
        items = tag_map[tag]
        links = " · ".join(
            f"[{a['title_zh']}]({a['path']})" for a in items
        )
        lines.append(f"- **{tag}**（{len(items)}）：{links}")
    lines.append("")
    lines.append("## 翻译与整理说明")
    lines.append("")
    lines.append("- 全文翻译力求忠实、完整；代码块保持原样；MCP、SDK、harness、function calling、prompt injection、compaction、sandbox、A2A 等技术术语保留英文。")
    lines.append("- 原文配图未逐一复制，而以简要文字说明代替，请以官方原文中的图表为准。")
    lines.append("- 部分官方页面含大量合作伙伴评价、产品演示轨迹或后续相关推荐，译文在不影响技术内容的前提下可能略作整理，并在文中注明，细节以原文为准。")
    lines.append("- 部分文章日后有官方更新或维护说明（例如产品合并、API 调整、模型权重更新），已在 YAML 页眉的 `updated` 字段或正文中注明。")
    lines.append("- 各篇 Markdown 使用统一的 YAML 页眉：`title_en`、`title_zh`、`company`、`date`、`updated`（可选）、`url`、`type`（`full` | `summary`）、`category`、`tags`（3–6 个）。")
    lines.append("")
    lines.append("## 版权与使用说明")
    lines.append("")
    lines.append(
        "各篇原文版权归其发表公司所有（Anthropic、OpenAI、Google / DeepMind、DeepSeek、Microsoft、Mistral、阿里通义、月之暗面、智谱、Meta 等）。"
        "本仓库中的中文翻译与摘要仅供个人学习与研究使用，不构成官方译本，也不主张对原文内容享有权利。"
        "请通过各篇页眉、目录表与阅读页中的原文链接阅读官方出处；转载或引用时请同时注明原作者与原文链接，并遵守各公司的使用条款。"
    )
    lines.append("")
    lines.append("如需引用或核对，一律以各公司官方页面为准。")
    lines.append("")
    lines.append("仓库名称仍为历史沿用的 `ai-agent-articles-zh`；内容已扩展为多公司文库。若需更名，可考虑 `ai-agent-articles-zh` 或 `agent-dev-articles-zh`（需仓库所有者另行决定，本构建脚本不会改名或改可见性）。")
    lines.append("")
    README.write_text("\n".join(lines), encoding="utf-8")


def render_body(body: str) -> str:
    MD.reset()
    return MD.convert(body)


def write_article_pages(arts: list[dict]) -> None:
    art_root = DOCS_DIR / "articles"
    if art_root.exists():
        shutil.rmtree(art_root)
    for a in arts:
        out = DOCS_DIR / a["html_path"]
        out.parent.mkdir(parents=True, exist_ok=True)
        body_html = render_body(a["body"])
        tags = "".join(
            f'<a class="chip" href="../../index.html?tag={escape_attr(t)}">{escape(t)}</a>'
            for t in a["tags"]
        )
        updated = (
            f'<p class="updated">更新日期：{escape(a["updated"])}</p>'
            if a["updated"]
            else ""
        )
        typ_cls = "full" if a["type"] == "full" else "sum"
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(a['title_zh'])} · {escape(a['company_zh'])}</title>
<link rel="stylesheet" href="../../styles.css">
</head>
<body>
<div class="wrap article-page">
  <nav class="crumb"><a href="../../index.html">← 返回文库首页</a></nav>
  <article class="{typ_cls}">
    <header>
      <p class="meta-row">
        <span class="co">{escape(a['company_zh'])}</span>
        <time datetime="{a['date']}">{a['date']}</time>
        <span class="kind {typ_cls}">{a['type_zh']}</span>
        <span class="cat">{escape(a['category'])}</span>
      </p>
      <h1>{escape(a['title_zh'])}</h1>
      <p class="en-title">{escape(a['title_en'])}</p>
      {updated}
      <p class="orig">原文：<a href="{escape_attr(a['url'])}" target="_blank" rel="noopener">{escape(a['url'])}</a></p>
      <p class="chips">{tags}</p>
    </header>
    <div class="body">{body_html}</div>
  </article>
  <footer class="site">原文版权归相应公司所有。中文翻译与摘要仅供个人学习，请以官方原文为准。</footer>
</div>
<script src="../../theme.js"></script>
</body>
</html>
"""
        out.write_text(html, encoding="utf-8")


def escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def escape_attr(s: str) -> str:
    return escape(s)


def write_css() -> None:
    (DOCS_DIR / "styles.css").write_text(
        r"""
:root {
  --bg: #f6f3ec;
  --card: #fffcf7;
  --ink: #1c1917;
  --muted: #57534e;
  --line: #e7e0d4;
  --accent: #9a3412;
  --accent-2: #1d4ed8;
  --chip: #f0ece4;
  --shadow: 0 1px 2px rgba(28,25,23,.06);
}
:root[data-theme="dark"] {
  --bg: #161412;
  --card: #1f1c19;
  --ink: #f5f0e8;
  --muted: #a8a29e;
  --line: #3f3a34;
  --accent: #fb923c;
  --accent-2: #93c5fd;
  --chip: #2a2622;
  --shadow: 0 1px 2px rgba(0,0,0,.35);
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
  background: var(--bg);
  color: var(--ink);
  font-family: "Source Han Serif SC", "Noto Serif SC", "Songti SC", "STSong", Georgia, serif;
  font-size: 17px;
  line-height: 1.75;
}
.wrap { max-width: 980px; margin: 0 auto; padding: 36px 20px 80px; }
header.hero { margin-bottom: 24px; }
header.hero h1 { font-size: 1.85rem; line-height: 1.3; margin: 0 0 10px; }
header.hero p { color: var(--muted); margin: 0 0 8px; }
.toolbar {
  display: flex; flex-wrap: wrap; gap: 10px; align-items: center;
  margin: 16px 0 10px;
}
.search {
  flex: 1 1 240px;
  font: inherit;
  font-family: "Source Han Sans SC", "Noto Sans SC", "PingFang SC", sans-serif;
  padding: 8px 12px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--card);
  color: var(--ink);
}
select.filter, button.theme-toggle {
  font-family: "Source Han Sans SC", "Noto Sans SC", "PingFang SC", sans-serif;
  font-size: .9rem;
  padding: 8px 10px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--card);
  color: var(--ink);
  cursor: pointer;
}
.stats { color: var(--muted); font-size: .92rem; margin: 8px 0 16px; }
.list { display: flex; flex-direction: column; gap: 12px; }
.card {
  display: block;
  text-decoration: none;
  color: inherit;
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 16px 18px 14px;
  box-shadow: var(--shadow);
}
.card:hover { border-color: var(--accent); }
.card h2 { font-size: 1.12rem; margin: 0 0 4px; line-height: 1.4;
  font-family: "Source Han Sans SC", "Noto Sans SC", "PingFang SC", sans-serif; }
.card .en { color: var(--muted); margin: 0 0 8px; font-size: .92rem; }
.meta-row { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin: 0 0 8px;
  font-family: "Source Han Sans SC", "Noto Sans SC", sans-serif; font-size: .85rem; }
.co { font-weight: 650; color: var(--accent); }
.kind { color: #fff; background: #9a3412; border-radius: 999px; padding: 1px 8px; font-size: .75rem; }
.kind.sum, .kind.summary { background: #57534e; }
:root[data-theme="dark"] .kind.full { background: #c2410c; }
.cat { color: var(--muted); }
.excerpt { margin: 0; color: var(--muted); font-size: .95rem; }
.chips { display: flex; flex-wrap: wrap; gap: 6px; margin: 8px 0 0; }
.chip {
  display: inline-block;
  font-family: "Source Han Sans SC", "Noto Sans SC", sans-serif;
  font-size: .78rem;
  background: var(--chip);
  color: var(--ink);
  border-radius: 999px;
  padding: 1px 10px;
  text-decoration: none;
  border: 1px solid transparent;
  cursor: pointer;
}
.chip:hover, .chip.active { border-color: var(--accent); color: var(--accent); }
.empty { color: var(--muted); padding: 32px 0; text-align: center; }
.crumb { margin: 0 0 18px; font-family: "Source Han Sans SC", "Noto Sans SC", sans-serif; }
.crumb a { color: var(--accent-2); text-decoration: none; }
.article-page article { background: var(--card); border: 1px solid var(--line); border-radius: 12px; padding: 28px 32px 40px; }
.article-page header { border-bottom: 1px solid var(--line); margin: 0 0 24px; padding: 0 0 16px; }
.article-page h1 { margin: 0 0 6px; font-size: 1.55rem; line-height: 1.3;
  font-family: "Source Han Sans SC", "Noto Sans SC", "PingFang SC", sans-serif; }
.en-title { color: var(--muted); margin: 0 0 8px; }
.orig, .updated { font-size: .92rem; color: var(--muted); word-break: break-all; }
.body h1, .body h2, .body h3, .body h4 {
  font-family: "Source Han Sans SC", "Noto Sans SC", "PingFang SC", sans-serif;
  line-height: 1.35; margin-top: 1.5em;
}
.body code {
  font-family: "IBM Plex Mono", "SF Mono", Menlo, Consolas, monospace;
  font-size: .88em; background: var(--chip); padding: .1em .35em; border-radius: 4px;
}
.body pre {
  background: #1c1917; color: #f5f0e8; padding: 14px 16px; border-radius: 8px;
  overflow-x: auto; font-size: .82rem; line-height: 1.5;
}
.body pre code { background: none; color: inherit; padding: 0; }
.body table { border-collapse: collapse; width: 100%; font-size: .92rem; margin: 1em 0;
  font-family: "Source Han Sans SC", "Noto Sans SC", sans-serif; }
.body th, .body td { border: 1px solid var(--line); padding: 6px 10px; vertical-align: top; }
.body th { background: var(--chip); text-align: left; }
.body blockquote { margin: 1em 0; padding: .2em 1em; border-left: 3px solid var(--accent); color: var(--muted); }
a { color: var(--accent-2); }
footer.site { color: var(--muted); font-size: .9rem; text-align: center; margin-top: 28px; }
@media (max-width: 640px) {
  .article-page article { padding: 20px 16px 28px; }
  header.hero h1 { font-size: 1.45rem; }
}
""".strip()
        + "\n",
        encoding="utf-8",
    )


def write_theme_js() -> None:
    (DOCS_DIR / "theme.js").write_text(
        """
(function () {
  const key = "agent-lib-theme";
  const saved = localStorage.getItem(key);
  const preferDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  const theme = saved || (preferDark ? "dark" : "light");
  document.documentElement.setAttribute("data-theme", theme);
  window.toggleTheme = function () {
    const next = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem(key, next);
    const btn = document.getElementById("theme-toggle");
    if (btn) btn.textContent = next === "dark" ? "浅色" : "深色";
  };
  document.addEventListener("DOMContentLoaded", function () {
    const btn = document.getElementById("theme-toggle");
    if (btn) btn.textContent = document.documentElement.getAttribute("data-theme") === "dark" ? "浅色" : "深色";
  });
})();
""".strip()
        + "\n",
        encoding="utf-8",
    )


def write_index() -> None:
    (DOCS_DIR / "index.html").write_text(
        """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI Agent 开发文章文库（中文整理）</title>
<link rel="stylesheet" href="styles.css">
<script src="theme.js"></script>
</head>
<body>
<div class="wrap">
  <header class="hero">
    <h1>AI Agent 开发文章文库</h1>
    <p>整理 Anthropic、OpenAI、Google / DeepMind、DeepSeek 等公司官方发布的 Agent 开发文章，附中文翻译或摘要。按时间从新到旧排列，可用公司、分类与标签筛选。</p>
  </header>
  <div class="toolbar">
    <input class="search" id="q" type="search" placeholder="搜索标题或摘要…" autocomplete="off">
    <select class="filter" id="company"><option value="">全部公司</option></select>
    <select class="filter" id="category"><option value="">全部分类</option></select>
    <button class="theme-toggle" id="theme-toggle" type="button" onclick="toggleTheme()">深色</button>
  </div>
  <div class="chips" id="tag-bar"></div>
  <p class="stats" id="stats"></p>
  <div class="list" id="list"></div>
  <footer class="site">原文版权归相应公司所有。中文翻译与摘要仅供个人学习，请以官方原文为准。</footer>
</div>
<script>
(function () {
  const $ = (id) => document.getElementById(id);
  const params = new URLSearchParams(location.search);
  let data = null;
  let activeTag = params.get("tag") || "";

  function applyParamsToControls() {
    if (params.get("company")) $("company").value = params.get("company");
    if (params.get("category")) $("category").value = params.get("category");
    if (params.get("q")) $("q").value = params.get("q");
  }

  function writeParams() {
    const p = new URLSearchParams();
    if ($("company").value) p.set("company", $("company").value);
    if ($("category").value) p.set("category", $("category").value);
    if (activeTag) p.set("tag", activeTag);
    if ($("q").value.trim()) p.set("q", $("q").value.trim());
    const qs = p.toString();
    history.replaceState(null, "", qs ? ("?" + qs) : location.pathname);
  }

  function esc(s) {
    return String(s).replace(/[&<>"']/g, (c) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
    }[c]));
  }

  function render() {
    if (!data) return;
    const company = $("company").value;
    const category = $("category").value;
    const q = $("q").value.trim().toLowerCase();
    const items = data.articles.filter((a) => {
      if (company && a.company !== company) return false;
      if (category && a.category !== category) return false;
      if (activeTag && !(a.tags || []).includes(activeTag)) return false;
      if (q) {
        const hay = [a.title_en, a.title_zh, a.excerpt, (a.tags || []).join(" "), a.company_zh, a.category].join(" ").toLowerCase();
        if (!hay.includes(q)) return false;
      }
      return true;
    });
    $("stats").textContent = "显示 " + items.length + " / " + data.articles.length + " 篇（全文翻译 " + data.counts.full + "，中文摘要 " + data.counts.summary + "）";
    if (!items.length) {
      $("list").innerHTML = '<p class="empty">没有符合条件的文章，请调整筛选。</p>';
      return;
    }
    $("list").innerHTML = items.map((a) => {
      const tags = (a.tags || []).map((t) => '<span class="chip' + (t === activeTag ? " active" : "") + '" data-tag="' + esc(t) + '">' + esc(t) + "</span>").join("");
      const updated = a.updated ? " · 更新 " + a.updated : "";
      return (
        '<a class="card" href="' + esc(a.html_path) + '">' +
          '<p class="meta-row">' +
            '<span class="co">' + esc(a.company_zh) + "</span>" +
            "<time>" + esc(a.date) + updated + "</time>" +
            '<span class="kind ' + a.type + '">' + esc(a.type_zh) + "</span>" +
            '<span class="cat">' + esc(a.category) + "</span>" +
          "</p>" +
          "<h2>" + esc(a.title_zh) + "</h2>" +
          '<p class="en">' + esc(a.title_en) + "</p>" +
          (a.excerpt ? '<p class="excerpt">' + esc(a.excerpt) + "</p>" : "") +
          '<p class="chips">' + tags + "</p>" +
        "</a>"
      );
    }).join("");
  }

  function renderTags() {
    const counts = {};
    data.articles.forEach((a) => (a.tags || []).forEach((t) => { counts[t] = (counts[t] || 0) + 1; }));
    const tags = Object.keys(counts).sort((a, b) => counts[b] - counts[a] || a.localeCompare(b, "zh"));
    $("tag-bar").innerHTML = tags.map((t) =>
      '<button type="button" class="chip' + (t === activeTag ? " active" : "") + '" data-tag="' + esc(t) + '">' + esc(t) + " · " + counts[t] + "</button>"
    ).join("");
  }

  function onTag(tag) {
    activeTag = (activeTag === tag) ? "" : tag;
    renderTags();
    render();
    writeParams();
  }

  document.addEventListener("click", (e) => {
    const el = e.target.closest("[data-tag]");
    if (!el) return;
    e.preventDefault();
    e.stopPropagation();
    onTag(el.getAttribute("data-tag"));
  });

  ["q", "company", "category"].forEach((id) => {
    $(id).addEventListener("input", () => { render(); writeParams(); });
    $(id).addEventListener("change", () => { render(); writeParams(); });
  });

  fetch("data/articles.json")
    .then((r) => {
      if (!r.ok) throw new Error("无法加载 data/articles.json");
      return r.json();
    })
    .then((d) => {
      data = d;
      d.companies.forEach((c) => {
        if ((d.counts.by_company[c.id] || 0) === 0) return;
        const opt = document.createElement("option");
        opt.value = c.id;
        opt.textContent = c.name_zh + "（" + d.counts.by_company[c.id] + "）";
        $("company").appendChild(opt);
      });
      d.categories.forEach((cat) => {
        const opt = document.createElement("option");
        opt.value = cat;
        opt.textContent = cat;
        $("category").appendChild(opt);
      });
      applyParamsToControls();
      renderTags();
      render();
    })
    .catch((err) => {
      $("stats").textContent = "加载失败：" + err.message + "。请通过本地 HTTP 服务打开 docs/ 目录（例如 python3 -m http.server）。";
    });
})();
</script>
</body>
</html>
""",
        encoding="utf-8",
    )


def main() -> None:
    arts = load_articles()
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    write_json(arts)
    write_readme(arts)
    write_css()
    write_theme_js()
    write_index()
    write_article_pages(arts)
    print(f"Built {len(arts)} articles")
    for k, *_ in COMPANIES:
        n = sum(1 for a in arts if a["company"] == k)
        if n:
            print(f"  {k}: {n}")


if __name__ == "__main__":
    main()
