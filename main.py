"""第三块：入口层。把前两层串起来，变成一个能用的命令行工具。

用法：
    python main.py https://example.com/some-article
    python main.py https://example.com/some-article -o 我的文章.md
"""

import argparse
import sys
from pathlib import Path
from urllib.parse import urlparse

from extract import extract
from fetch import FetchError, fetch_html


def default_filename(url: str) -> str:
    """从网址里猜一个文件名：/blog/2024/hello-world -> hello-world.md"""
    path = urlparse(url).path.rstrip("/")
    name = path.rsplit("/", 1)[-1] or "page"
    name = "".join(ch for ch in name if ch.isalnum() or ch in "-_") or "page"
    return f"{name}.md"


def main() -> int:
    # Windows 控制台默认编码是 GBK（cp936）。如果标题里有 GBK 编不出来的字符
    # （比如 ¶ 、emoji、某些欧洲字母），print 会直接抛 UnicodeEncodeError 崩溃。
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="把网页正文保存成 markdown 文件")
    parser.add_argument("url", help="要转换的网页地址")
    parser.add_argument("-o", "--output", help="输出文件名（默认按网址猜）")
    args = parser.parse_args()

    try:
        print(f"正在抓取 {args.url} ...")
        html = fetch_html(args.url)
        print(f"→ 抓到 HTML：{len(html):,} 字符")

        title, body = extract(html)
        print(f"→ 识别标题：{title}")

        # 有些网页的正文本身就带着 H1，再加一个标题就会重复两遍。
        heading = "" if body.lstrip().startswith("# ") else f"# {title}\n\n"
        content = f"{heading}> 来源：{args.url}\n\n{body}"

        out = Path(args.output or default_filename(args.url))
        # encoding="utf-8" 必须写：Windows 默认是 GBK，写中文会炸
        out.write_text(content, encoding="utf-8")
        print(f"→ 已写入 {out.resolve()}（{len(content):,} 字符）")
        return 0

    except FetchError as exc:
        print(f"抓取失败：{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())