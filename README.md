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

## 站点体系

统一入口：<https://aliucrazy.com/sites/>。博客与定制日历继续分别由原 GitHub 仓库维护及 GitHub Pages 发布，域名、DNS 和发布方式保持不变。

- 博客：<https://aliucrazy.com/>，源码 `aliucrazy/keli-blog`
- THE QGM CLUB 定制日历：<https://gift.aliucrazy.com/>，源码 `aliucrazy/gift`

`data/sites.json` 是站点清单的唯一来源，`layouts/shortcodes/site-directory.html` 在构建时渲染 `/sites/`，无需浏览器脚本或外部 API。清单字段：`id` 为唯一标识，`name` / `description` 为展示文案，`url` / `domain` 为正式入口，`repository` / `branch` 为源码位置，`hosting` / `publishing` 为部署方式，`actions_url` / `settings_url` 为 GitHub 管理入口。所有字段均为公开信息，不得写入令牌或其他凭证。

维护站点时更新清单，运行 `hugo --gc --minify`，检查 `/sites/` 及导航后推送 `main`，由既有 Actions 自动部署。新增或更换域名需另行配置，修改清单不会自动修改 DNS。

这是统一导航与管理快捷入口，不提供跨仓库部署控制或实时可用性监控。发布是否成功以各仓库 GitHub Actions / Pages 的结果为准。

回滚：在发生变更的仓库中对相应提交执行 `git revert <commit>`，推送后由原部署方式发布。礼物站的返回导航链接在 `gift/index.html` 页脚维护；该站不复制站点清单。
