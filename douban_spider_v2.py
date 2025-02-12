import requests
from bs4 import BeautifulSoup
import csv
import time
import random
from urllib.parse import quote
import re
import urllib.parse


def search_book_id(book_name):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Cookie": "Cookie",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }

    # 修改为豆瓣主搜索页面
    search_url = "https://www.douban.com/search"
    params = {"cat": "1001", "q": book_name}  # 书籍分类

    try:
        response = requests.get(search_url, headers=headers, params=params, timeout=15)
        response.encoding = "utf-8"
        soup = BeautifulSoup(response.text, "html.parser")

        # 新解析逻辑：遍历所有链接
        for a in soup.find_all("a", href=True):
            href = a["href"]

            # 方式1：直接匹配常规链接
            direct_match = re.search(
                r"//(?:m\.)?book\.douban\.com/subject/(\d+)/", href
            )
            if direct_match:
                return direct_match.group(1)

            # 方式2：处理跳转链接
            if "link2" in href:
                parsed_url = urllib.parse.urlparse(href)
                qs = urllib.parse.parse_qs(parsed_url.query)
                if "url" in qs:
                    real_url = urllib.parse.unquote(qs["url"][0])
                    jump_match = re.search(r"subject/(\d+)/", real_url)
                    if jump_match:
                        return jump_match.group(1)

        print("未找到有效书籍链接")
        return None

    except Exception as e:
        print(f"搜索失败: {str(e)}")
        return None


def get_book_comments(book_id, max_pages=10):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": f"https://book.douban.com/subject/{book_id}/",
    }

    base_url = f"https://book.douban.com/subject/{book_id}/comments/"
    comments = []
    page_count = 0

    while page_count < max_pages:
        params = {"start": page_count * 20, "limit": 20, "status": "P", "sort": "score"}

        try:
            response = requests.get(
                base_url, headers=headers, params=params, timeout=15
            )
            soup = BeautifulSoup(response.text, "html.parser")

            items = soup.select(".comment-item")
            if not items:
                break

            for item in items:
                try:
                    comment = {
                        "user": item.select_one(".comment-info a").text.strip(),
                        "rating": (
                            item.select_one(".rating")["title"]
                            if item.select_one(".rating")
                            else "无"
                        ),
                        "content": item.select_one(".comment-content").text.strip(),
                        "votes": (
                            item.select_one(".vote-count").text
                            if item.select_one(".vote-count")
                            else "0"
                        ),
                        "time": item.select_one(".comment-time").text.strip(),
                    }
                    comments.append(comment)
                except Exception as e:
                    print(f"解析评论出错: {str(e)}")
                    continue

            page_count += 1
            print(f"已抓取第 {page_count} 页，累计 {len(comments)} 条评论")

            # 随机延迟防止封禁
            time.sleep(random.uniform(2, 5))

        except Exception as e:
            print(f"抓取第 {page_count+1} 页失败: {str(e)}")
            break

    return comments


def save_to_csv(comments, filename):
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f, fieldnames=["user", "rating", "content", "votes", "time"]
        )
        writer.writeheader()
        writer.writerows(comments)


if __name__ == "__main__":
    book_name = input("请输入要爬取的书名：").strip()

    print("正在搜索书籍ID...")
    book_id = search_book_id(book_name)

    if not book_id:
        print("未找到相关书籍，请尝试手动输入ID")
        book_id = input("请输入书籍ID（例如4913064）：").strip()

    print(f"开始爬取【{book_name}】的评论（ID: {book_id}）...")
    comments = get_book_comments(book_id, max_pages=10)

    if comments:
        filename = f"{book_name}_评论.csv"
        save_to_csv(comments, filename)
        print(f"成功保存{len(comments)}条评论到 {filename}")
    else:
        print("未找到评论数据")
