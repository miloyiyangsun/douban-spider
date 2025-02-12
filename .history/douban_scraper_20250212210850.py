import requests
from bs4 import BeautifulSoup
import time
import random


def get_comments_from_url(url):
    """
    根据给定url获取当前页的评论列表
    参数:
        url: 评论页面的完整链接，如 "https://book.douban.com/subject/xxxxxxxx/comments/?start=0"
    返回:
        评论内容文本列表
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
        " Chrome/110.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
    except Exception as e:
        print(f"请求失败：{e}")
        return []

    if response.status_code != 200:
        print(f"请求失败，状态码：{response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    # 根据豆瓣书评页结构，每个评论通常位于 <div class="comment-item"> 内部的 <p class="comment-content">
    comment_items = soup.find_all("div", class_="comment-item")
    comments = []
    for item in comment_items:
        comment_tag = item.find("p", class_="comment-content")
        if comment_tag:
            # 有时评论内容中可能含有换行符、空格，可以用strip()处理
            comments.append(comment_tag.get_text(strip=True))
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
    # 示例用法：
    # 请将book_id替换为你想要爬取的豆瓣书籍ID，例如 "1084336"
    book_id = input("请输入豆瓣书籍ID：").strip()
    max_pages = input("请输入希望爬取的页数（默认10页）：").strip()
    max_pages = int(max_pages) if max_pages.isdigit() else 10

    reviews = scrape_reviews(book_id, max_pages)
    print(f"\n共获取 {len(reviews)} 条评论：")
    for idx, comment in enumerate(reviews, start=1):
        print(f"{idx}. {comment}")
