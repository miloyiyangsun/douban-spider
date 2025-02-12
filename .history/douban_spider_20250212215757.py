import requests
from bs4 import BeautifulSoup
import csv
import time


def get_book_comments(book_id):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    base_url = f"https://book.douban.com/subject/{book_id}/comments/"
    comments = []

    # 自动翻页逻辑
    start = 0
    while True:
        params = {"start": start, "limit": 20, "status": "P", "sort": "score"}

        try:
            response = requests.get(
                base_url, headers=headers, params=params, timeout=10
            )
            soup = BeautifulSoup(response.text, "html.parser")

            # 解析评论项
            items = soup.select(".comment-item")
            if not items:
                break

            for item in items:
                comment = {
                    "user": item.select_one(".comment-info a").text.strip(),
                    "rating": (
                        item.select_one(".user-stars")["title"]
                        if item.select_one(".user-stars")
                        else "无评分"
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

            # 检查是否有下一页
            next_page = soup.select_one("a.next")
            if not next_page:
                break

            start += 20
            time.sleep(2)  # 防止请求过快

        except Exception as e:
            print(f"抓取出错: {str(e)}")
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
    book_id = input("请输入书籍ID（例如4913064）：").strip()

    print("开始爬取评论...")
    comments = get_book_comments(book_id)

    if comments:
        filename = f"{book_name}_评论.csv"
        save_to_csv(comments, filename)
        print(f"成功保存{len(comments)}条评论到 {filename}")
    else:
        print("未找到评论数据")
