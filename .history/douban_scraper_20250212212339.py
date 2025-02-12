import requests
from bs4 import BeautifulSoup
import time
import random
import re
import urllib.parse  # 新增：用于解析跳转链接


def search_book_id_by_name(book_name):
    """
    根据给定的书名搜索并返回豆瓣书籍的ID
    参数:
        book_name: 待搜索的书名
    返回:
        豆瓣书籍的ID，字符串类型；如果搜索不到则返回 None
    """
    search_url = "https://www.douban.com/search"
    params = {"cat": "1001", "q": book_name}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/110.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(search_url, params=params, headers=headers, timeout=10)
    except Exception as e:
        print(f"搜索请求失败：{e}")
        return None

    print("搜索请求成功，状态码：", response.status_code)
    if response.status_code != 200:
        print(f"搜索请求失败，状态码：{response.status_code}")
        return None

    # 调试：打印响应的前1000个字符，确认页面内容是否正确返回
    snippet = response.text[:1000]
    print("响应内容前1000字符：\n", snippet)

    soup = BeautifulSoup(response.text, "html.parser")
    a_tags = soup.find_all("a", href=True)
    print(f"共找到 {len(a_tags)} 个链接")
    for a in a_tags:
        href = a["href"]
        print("调试链接：", href)
        # 先直接尝试匹配正常形式的链接
        match = re.search(r"//(?:m\.)?book\.douban\.com/subject/(\d+)/", href)
        if match:
            print("匹配成功，找到书籍ID：", match.group(1))
            return match.group(1)
        # 如果链接中包含跳转链接，则解析参数中的真实链接
        elif "link2" in href:
            parsed_url = urllib.parse.urlparse(href)
            qs = urllib.parse.parse_qs(parsed_url.query)
            if "url" in qs:
                real_url = qs["url"][0]
                real_url = urllib.parse.unquote(real_url)  # 解码真实链接
                print("解码后的真实链接：", real_url)
                match = re.search(
                    r"//(?:m\.)?book\.douban\.com/subject/(\d+)/", real_url
                )
                if match:
                    print("匹配成功，从 link2 链接中找到书籍ID：", match.group(1))
                    return match.group(1)
    print("没有找到该书的ID，请确认书名是否正确。")
    return None


def get_comments_from_url(url):
    """
    根据给定URL获取当前页的评论列表
    参数:
        url: 评论页面的完整链接，如 "https://book.douban.com/subject/xxxxxxxx/comments/?start=0"
    返回:
        评论内容文本列表
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
        " Chrome/110.0.0.0 Safari/537.36",
        # 添加更多headers以模拟浏览器行为
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Connection": "keep-alive",
        "Cookie": "bid="
        + "".join(random.choices("0123456789abcdef", k=11)),  # 随机生成bid
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"评论页面响应状态码：{response.status_code}")
        print("评论页面响应内容片段：")
        print(response.text[:500])  # 打印响应内容的前500个字符
    except Exception as e:
        print(f"请求失败：{e}")
        return []

    if response.status_code != 200:
        print(f"请求失败，状态码：{response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    # 打印页面结构信息
    print("\n查找评论区域...")
    comment_items = soup.find_all("div", class_="comment-item")
    print(f"找到 {len(comment_items)} 个评论项")

    comments = []
    for item in comment_items:
        comment_tag = item.find("p", class_="comment-content")
        if comment_tag:
            comment_text = comment_tag.get_text(strip=True)
            print(f"找到评论：{comment_text[:50]}...")  # 打印评论预览
            comments.append(comment_text)
        else:
            print("在评论项中未找到评论内容标签")

    return comments


def scrape_reviews(book_id, max_pages=10):
    """
    根据对应书籍的豆瓣ID爬取评论
    参数:
        book_id: 豆瓣书籍的ID，例如 "1084336"（不同书籍的ID不同）
        max_pages: 最大爬取的页数（每页一般有20条评论），默认为10页
    返回:
        返回所有收集的评论列表
    """
    all_comments = []
    base_url = f"https://book.douban.com/subject/{book_id}/comments/"
    for page in range(max_pages):
        start = page * 20  # 豆瓣评论翻页参数
        url = f"{base_url}?start={start}"
        print(f"正在爬取: {url}")
        comments = get_comments_from_url(url)
        if not comments:
            print("该页没有获取到评论，可能已经爬取完毕或遇到反爬策略。")
            break
        all_comments.extend(comments)
        # 随机延时，减少被封IP的风险
        time.sleep(random.uniform(1, 3))
    return all_comments


if __name__ == "__main__":
    # 示例用法：直接输入书名，程序会搜索出对应书籍的ID，再获取评论
    book_name = input("请输入豆瓣书籍名称：").strip()
    book_id = search_book_id_by_name(book_name)
    if not book_id:
        print("未能找到对应的书籍ID，请确认书名是否正确。")
    else:
        print(f"搜索到书籍ID: {book_id}")
        max_pages = input("请输入希望爬取的页数（默认10页）：").strip()
        max_pages = int(max_pages) if max_pages.isdigit() else 10

        reviews = scrape_reviews(book_id, max_pages)
        print(f"\n共获取 {len(reviews)} 条评论：")
        for idx, comment in enumerate(reviews, start=1):
            print(f"{idx}. {comment}")
