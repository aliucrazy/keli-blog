# keli-blog — 克礼的个人博客

Hugo 静态博客（`beautifulhugo` 主题），GitHub Actions 自动构建并部署到 GitHub Pages。

- 本地预览：`hugo server -D`
- 生产构建：`hugo --gc --minify`
- 发布：push 到 `main` 分支即自动部署

## 写文章

在 `content/post/{年份}/` 下新建 `{编号}-{slug}.md`，frontmatter：

```yaml
---
title: "标题"
subtitle: "副标题（可选）"
date: 2026-09-28
tags: ["tag1", "tag2"]
---
```

正文开头段落后用 `<!--more-->` 分隔摘要。编号按年份递增（参考现有文章的最大编号）。

## 内容管线（采集 → 成文 → 发布）

1. **采集**：把想写的文章/论文链接发给 Muse（或由每周论文检查自动发现）
2. **成文**：Muse 深读后按"声称解法 / 可借鉴技巧 / 致命缺陷"写成中文综述，落到日常工作清单
3. **发布**：写成 `content/post/` 下的 Markdown 并推送到本仓库，Actions 自动部署
