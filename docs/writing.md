# 写一篇：六步，每步一条命令

## 1 定选题

克礼口述三到五分钟，我出提纲：标题、副标题、四节小标题、每节一句判断。
提纲点头后再动笔。没点头不写正文。

## 2 建骨架

    python3 scripts/new_post.py 005-harness-module-boundary --title "文章标题" --subtitle "一句话副标题"

编号自动取现有最大值加一。产出 `content/post/2026/005-.../index.md`。

判据：文件存在，`draft: true`，编号不撞车。

## 3 写正文

规矩四条：

1. 开头三句给结论。读者只看第一段也能拿走东西。
2. 每节第一句是判断，不是背景。
3. 单篇 1500 到 3500 字。超过就拆两篇。
4. 引数据标来源，标不出的写成「我的主张」。

## 4 配图

    python3 scripts/compress_img.py 截图.png --outdir content/post/2026/005-harness-module-boundary

长边超 1600 自动缩，一律转 webp，质量 82。单图目标小于 300 KB。

在正文里这样引，不用写完整路径：

    ![图 1 判定链](fig1.png)

判据：目录里只有 webp，页面里图不糊、不拉伸。

## 5 本地预览

    hugo server -D

打开 http://localhost:1313 。看三样：首页摘要、文章页版式、图是否清晰。

## 6 发布

    git checkout -b post/005-harness-module-boundary
    git add content/post/2026/005-harness-module-boundary
    git commit -m "post: 文章标题"
    git push -u origin post/005-harness-module-boundary
    gh pr create --fill

克礼点合并，CI 自动部署。合并后我验三处：线上标题、图、RSS 里有没有这篇。

判据：`/post/2026/005-.../` 返回 200，`/index.xml` 里有这篇。

## 卡住时

- 图糊：原图分辨率不够，回去要原图，别放大。
- 构建失败：先看 `hugo server` 的报错，再看 CI 日志，两边报错通常在同一行。
- 编号冲突：`new_post.py` 会自动避开，冲突说明手改了目录名。
