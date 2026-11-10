"""第一块：网络层。把 "网址" 变成 "HTML 字符串"。

这一层的职责只有一个：把网页的源代码下载回来。
它不负责解析、不负责转换 —— 那是下一层的事。
"""

import sys

import requests

# 伪装成浏览器。有些网站看到没有 User-Agent 的请求会直接 403。
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


class FetchError(Exception):
    """抓取失败时抛出的自定义异常，让上层用一句统一的话处理所有失败。"""


def fetch_html(url: str, timeout: int = 20) -> str:
    """下载网页，返回 HTML 文本。失败时抛 FetchError。"""
    try:
        # timeout 必须有：否则对方不回应时，你的程序会永远卡住。
        resp = requests.get(url, headers=HEADERS, timeout=timeout)
    except requests.RequestException as exc:
        # 断网、DNS 解析失败、超时、SSL 证书错误……都会走到这里
        raise FetchError(f"网络请求失败：{exc}") from exc

    if resp.status_code != 200:
        raise FetchError(
            f"服务器返回 {resp.status_code}（{resp.reason}），这个地址可能不存在或不让访问"
        )

    # 编码问题：HTTP 头里的 encoding 有时是错的（尤其是中文站）。
    if resp.encoding is None or resp.encoding.lower() == "iso-8859-1":
        resp.encoding = resp.apparent_encoding

    return resp.text


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python fetch.py <网址>")
        raise SystemExit(2)

    html = fetch_html(sys.argv[1])
    print(f"抓到 {len(html):,} 个字符")
    print("-" * 40)
    print(html[:500])