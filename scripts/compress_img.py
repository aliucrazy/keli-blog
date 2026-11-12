#!/usr/bin/env python3
"""把图压成 webp：长边不超过 1600，质量 82。省流量也省仓库额度。

用法：
    python3 scripts/compress_img.py 图1.png 图2.jpg
    python3 scripts/compress_img.py 图目录/*.png --outdir content/post/2026/005-xxx

不给 --outdir 就写在原图同目录，文件名换成 .webp。
已经小于 1600 宽的不放大，只转格式。
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

LONG_EDGE = 1600
QUALITY = 82


def width_of(path: Path) -> int:
    out = subprocess.run(
        ["sips", "-g", "pixelWidth", str(path)],
        capture_output=True, text=True, check=True).stdout
    return int(out.strip().split()[-1])


def convert(src: Path, outdir: Path | None) -> Path:
    target_dir = outdir or src.parent
    target_dir.mkdir(parents=True, exist_ok=True)
    dst = target_dir / (src.stem + ".webp")
    cmd = ["cwebp", "-q", str(QUALITY)]
    if width_of(src) > LONG_EDGE:
        cmd += ["-resize", str(LONG_EDGE), "0"]
    cmd += [str(src), "-o", str(dst)]
    subprocess.run(cmd, check=True, capture_output=True)
    saved = 100 - round(dst.stat().st_size * 100 / src.stat().st_size)
    print("%s -> %s  (%d KB, 省 %d%%)" % (
        src.name, dst.name, dst.stat().st_size // 1024, saved))
    return dst


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("images", nargs="+")
    ap.add_argument("--outdir")
    a = ap.parse_args()
    outdir = Path(a.outdir) if a.outdir else None
    failed = 0
    for name in a.images:
        src = Path(name)
        if not src.exists():
            print("跳过，找不到：%s" % src, file=sys.stderr)
            failed += 1
            continue
        convert(src, outdir)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
