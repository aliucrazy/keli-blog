#!/usr/bin/env python3
"""新建一篇博客：建目录、写骨架、留图位。

用法：
    python3 scripts/new_post.py 005-harness-module-boundary --title "文章的标题"

产物：
    content/post/2026/005-harness-module-boundary/index.md
    content/post/2026/005-harness-module-boundary/  （图放这里）

编号自动取现有最大值加一，不用手填。
"""
from __future__ import annotations

import argparse
import datetime
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
YEAR = datetime.date.today().year
POSTS = ROOT / "content" / "post" / str(YEAR)

TEMPLATE = """---
title: "{title}"
subtitle: "{subtitle}"
date: {date}
tags: []
draft: true
---

<!-- 开头先给结论，三句以内。读者只看这一段也能拿走东西。 -->

## 一、问题

## 二、我怎么做的

## 三、结果与代价

## 四、还没解决的
"""


def next_number(parent: Path) -> str:
    nums = []
    if parent.exists():
        for child in parent.iterdir():
            m = re.match(r"^(\d{3})-", child.name)
            if m:
                nums.append(int(m.group(1)))
    return "%03d" % (max(nums) + 1 if nums else 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug", help="英文短横线，不含编号，例如 harness-module-boundary")
    ap.add_argument("--title", required=True)
    ap.add_argument("--subtitle", default="")
    a = ap.parse_args()

    slug = a.slug.strip().lower()
    if re.search(r"[\s/]", slug):
        sys.exit("slug 不能有空格或斜杠")
    numbered = "%s-%s" % (next_number(POSTS), slug)
    bundle = POSTS / numbered
    if bundle.exists():
        sys.exit("已存在：%s" % bundle)

    bundle.mkdir(parents=True)
    text = TEMPLATE.format(
        title=a.title,
        subtitle=a.subtitle,
        date=datetime.date.today().isoformat(),
    )
    (bundle / "index.md").write_text(text, encoding="utf-8")
    print(bundle / "index.md")


if __name__ == "__main__":
    main()
