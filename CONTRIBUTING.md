# Contributing Guide / 贡献指南

Thank you for your interest in contributing to the O-RAN Expert Knowledge Base! / 感谢您对 O-RAN 专家知识库的贡献兴趣!

This repository is a bilingual (English / Chinese) documentation project. Please read the guidelines below before submitting changes. / 本仓库是中英双语文档项目,提交变更前请阅读以下规范。

---

## Directory Naming / 目录编号规范

- Top-level topic directories use a **two-digit number prefix followed by an English kebab-case name**: `NN-topic-name`, e.g. `01-architecture-system/`, `31-ai-ran-convergence/`.
  顶层主题目录采用 **两位数字编号 + 英文短横线(kebab-case)命名**:`NN-topic-name`,例如 `01-architecture-system/`、`31-ai-ran-convergence/`。
- Sub-directories use English kebab-case names without numbering: `ric-architecture/`, `energy-efficiency/`.
  子目录使用不带编号的英文短横线命名:`ric-architecture/`、`energy-efficiency/`。
- Choose the next available number when adding a new top-level topic; do not renumber existing directories.
  新增顶层主题时取下一个可用编号,不要对已有目录重新编号。

## Bilingual Readme Files / 双语 readme 文件

- Every topic directory **must** contain both:
  每个主题目录 **必须** 同时包含:
  - `readme.md` — English version(英文版)
  - `readme-zh.md` — Chinese translation(中文互译版)
- The two files should mirror each other in structure and content. When you update one, update the other in the same PR.
  两个文件在结构和内容上应相互对应;修改其中一个时,请在同一 PR 中同步更新另一个。

## Frontmatter / 前置元数据

Every Markdown document must start with a YAML frontmatter block containing the following required fields:
每篇 Markdown 文档必须以包含以下必填字段的 YAML frontmatter 开头:

| Field | 说明 |
|---|---|
| `title` | Document title / 文档标题 |
| `description` | One-sentence summary / 一句话摘要 |
| `category` | Content category, e.g. `documentation` / 内容分类 |
| `language` | `en-US` or `zh-CN` |
| `version` | Content version, e.g. `"1.0"` / 内容版本 |
| `last_updated` | ISO date, e.g. `"2026-09-03"` / 更新日期 |
| `keywords` | List of keywords / 关键词列表 |

Example / 示例:

```yaml
---
title: "O-RAN Architecture System"
description: "O-RAN layered architecture, functional distribution, and O-Cloud overview."
category: "documentation"
language: "en-US"
version: "1.0"
last_updated: "2026-09-03"
keywords: ['O-RAN', 'architecture', 'O-Cloud']
---
```

## Internal Links / 内部相对链接

- Use **relative links** for all internal references, not absolute paths.
  内部引用一律使用 **相对链接**,不要使用绝对路径。
- From the repository root, reference a document directly: `[E2 Interface](03-interface-standards/e2-interface.md)`.
  在根目录文档中直接引用:`[E2 接口](03-interface-standards/e2-interface.md)`。
- From a **sub-directory**, referencing another top-level directory requires going up two levels with `../../`, because the path is relative to the file, not the repo root:
  **子目录中的文件** 引用其他顶层目录时,需要先用 `../../` 返回两级(相对路径基于文件所在位置,而非仓库根):
  - From `07-ric-development/ric-architecture/xxx.md` to `03-interface-standards/e2-interface.md`:
    `[E2 Interface](../../03-interface-standards/e2-interface.md)`
- Always verify links resolve correctly in your PR preview.
  提交前请确认链接在 PR 预览中可以正常跳转。

## Commit Messages / 提交信息约定

Use conventional prefixes / 使用约定式前缀:

- `feat:` — new topic directory or major new content / 新增主题目录或重要新内容
- `docs:` — documentation additions or improvements / 文档内容新增或改进
- `fix:` — corrections, broken links, typos / 修正错误、失效链接、错别字

Examples / 示例:

```
feat: add 36-openran-6g chapter
docs: update e2-interface service model section
fix: broken relative links in 07-ric-development
```

## Submission Process / 提交流程

1. Fork the repository and create a feature branch. / Fork 本仓库并创建特性分支。
2. Make your changes following the guidelines above. / 按上述规范完成修改。
3. **Before opening a PR, run the validation script and make sure it passes:**
   **提交 PR 之前,务必运行校验脚本并确保通过:**

   ```bash
   python3 scripts/validate.py
   ```

4. Open a Pull Request. CI will run the same validation; PRs failing CI will not be merged.
   提交 Pull Request。CI 会执行同样的校验,未通过 CI 的 PR 不会被合并。
5. Keep PRs focused: one topic or fix per PR. / 保持 PR 聚焦:一个 PR 只做一件事。

---

## License / 许可证

By contributing, you agree that your contributions will be licensed under the [Creative Commons Attribution 4.0 International (CC BY 4.0)](LICENSE) license.
提交贡献即表示您同意您的贡献内容采用 [Creative Commons Attribution 4.0 International (CC BY 4.0)](LICENSE) 许可证授权。
