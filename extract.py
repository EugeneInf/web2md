"""第二块：解析层。把 "一整页 HTML" 变成 "干净的正文 markdown"。

难点不在转换，而在"哪一段才是正文"。
HTML 里没有哪个标签写着"正文在此"，所以只能用启发式去猜。
"""

from bs4 import BeautifulSoup
from markdownify import markdownify

# 这些标签装的是"网页的零件"（导航、页脚、广告、脚本），不是文章。
JUNK_TAGS = [
    "script", "style", "noscript", "nav", "header", "footer",
    "aside", "form", "iframe", "svg", "button",
]

# 各种网站最可能用来包文章的容器，按"可信度"从高到低排。
CANDIDATE_SELECTORS = [
    "article",
    "main",
    "[role=main]",
    ".article-content",
    ".post-content",
    ".markdown-body",
    ".entry-content",
    "#content",
]


def _pick_main(soup):
    """猜哪一块是正文。返回一个 BeautifulSoup 节点。"""
    for selector in CANDIDATE_SELECTORS:
        node = soup.select_one(selector)
        # 光有标签不够：有些站的 <article> 里只有一句话。
        if node and len(node.get_text(strip=True)) > 200:
            return node

    # 兜底：谁的 <p> 最多，谁最像正文。
    best_node, best_score = None, 0
    for node in soup.find_all(["div", "section", "td"]):
        score = len(node.find_all("p"))
        if score > best_score:
            best_node, best_score = node, score
    return best_node or soup.body or soup


def _guess_title(soup) -> str:
    """标题优先取 H1，没有就用 <title>。"""
    h1 = soup.find("h1")
    if h1 and h1.get_text(strip=True):
        title = h1.get_text(strip=True)
    elif soup.title and soup.title.string:
        title = soup.title.string.strip()
    else:
        return "未命名页面"

    # 真实网页的标题里常带排版符号，比如文档站的 H1 末尾有 ¶（段落锚点）。
    return title.replace("\u00b6", "").strip() or "未命名页面"


def _tidy(markdown: str) -> str:
    """收尾：去掉行尾空格，把连续空行压成一个。"""
    cleaned: list[str] = []
    for line in markdown.split("\n"):
        line = line.rstrip()
        if line == "" and cleaned and cleaned[-1] == "":
            continue
        cleaned.append(line)
    return "\n".join(cleaned).strip() + "\n"


def extract(html: str) -> tuple[str, str]:
    """返回 (标题, markdown 正文)。"""
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(JUNK_TAGS):
        tag.decompose()

    title = _guess_title(soup)
    main = _pick_main(soup)

    md = markdownify(str(main), heading_style="ATX")
    return title, _tidy(md)