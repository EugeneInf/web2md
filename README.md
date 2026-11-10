# web2md

把网页正文保存成干净的 markdown 文件。

给它一个网址，它下载 HTML、去掉导航和脚本、猜出正文，写成 `.md`。

## 安装

需要 Python 3.10+（代码里用了 `list[str]`、`tuple[str, str]` 这种类型标注）。

```
python -m pip install requests beautifulsoup4 markdownify
```

国内网络慢就加清华镜像：

```
python -m pip install requests beautifulsoup4 markdownify -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 用法

```
python main.py <网址>
python main.py <网址> -o 我的文章.md
```

例：

```
python main.py https://docs.python.org/3/tutorial/controlflow.html
```

输出：

```
正在抓取 https://docs.python.org/3/tutorial/controlflow.html ...
→ 抓到 HTML：140,035 字符
→ 识别标题：4.More Control Flow Tools
→ 已写入 D:\...\controlflowhtml.md（41,755 字符）
```

不写 `-o` 时，文件名从网址最后一段猜（`/tutorial/controlflow.html` → `controlflowhtml.md`）。

## 工作原理

1. `fetch.py` —— 发 HTTP GET 下载 HTML，处理 User-Agent、超时、状态码和编码，失败统一抛 `FetchError`。
2. `extract.py` —— 用 BeautifulSoup 把 HTML 解析成 DOM 树，删掉 `script / nav / footer` 这些噪音，按选择器启发式猜出正文，再用 markdownify 转成 markdown。
3. `main.py` —— 用 argparse 收参数，把前两步串起来，写文件。

三层分开的好处：每层都能单独跑、单独测、单独替换。

## 已知限制

- 抓不了 JS 渲染出来的内容（`requests` 只拿服务器返回的初始 HTML）。
- 有些站点首页 / 列表页没有「正文」，提取结果可能是一堆链接。
- 反爬站点会返回 403 或空内容。
- 不下载图片，不修正相对链接。
- 正文判定靠启发式，论坛帖、商品页这类结构特殊的页面可能猜错。

## 我在这上面学到的东西

- **分层**：网络 / 解析 / 入口，每层只干一件事，出错时能立刻定位是哪一层的锅。
- **编码**：`requests` 的 `resp.encoding` 有时是错的（中文站尤其），要用 `apparent_encoding` 兜底；写文件必须显式 `encoding="utf-8"`。
- **异常封装**：底层抛具体异常，上层统一处理；`raise ... from exc` 保留原始堆栈。
- **启发式**：HTML 里没有「正文在此」的标记，只能靠选择器 + 长度阈值去猜。
- **先离线再在线**：先用本地假页面（`_fixture.html`）验证解析，才能把「网络问题」和「代码问题」分开。
