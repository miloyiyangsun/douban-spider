import scrapy
from scrapy.crawler import CrawlerProcess
import random
import time
from bs4 import BeautifulSoup
import json


class DoubanBookSpider(scrapy.Spider):
    name = "douban_book"
    allowed_domains = ["book.douban.com"]

    def __init__(self, book_id=None, *args, **kwargs):
        super(DoubanBookSpider, self).__init__(*args, **kwargs)
        self.book_id = book_id
        self.comments = []

    def start_requests(self):
        # 构造请求头
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Connection": "keep-alive",
            "Host": "book.douban.com",
            "Referer": f"https://book.douban.com/subject/{self.book_id}/",
            "Cookie": f"bid={''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=11))}; __utmz=1;",
        }

        # 构造评论页面URL
        base_url = f"https://book.douban.com/subject/{self.book_id}/comments/"

        # 爬取前5页评论
        for page in range(5):
            start = page * 20
            url = f"{base_url}?start={start}&limit=20&status=P&sort=new_score"
            yield scrapy.Request(
                url=url,
                headers=headers,
                callback=self.parse_comments,
                meta={"page": page + 1},
            )
            # 添加随机延时
            time.sleep(random.uniform(1, 3))

    def parse_comments(self, response):
        page = response.meta["page"]
        print(f"正在解析第 {page} 页评论...")

        # 使用BeautifulSoup解析页面
        soup = BeautifulSoup(response.text, "html.parser")
        comment_items = soup.find_all("li", class_="comment-item")

        for item in comment_items:
            # 使用更稳健的选择器写法
            comment = item.find("span", class_="short")
            if not comment:  # 增加防御性判断
                continue

            comment_text = comment.get_text(strip=True)

            # 更新用户选择器（豆瓣现在使用class="comment-info"）
            user_link = item.find("div", class_="comment-info").find("a")
            user = user_link.get_text(strip=True) if user_link else "匿名用户"

            # 更新评分选择器（使用data-rating属性更可靠）
            rating_span = item.find("span", class_="rating")
            rating = rating_span["data-rating"] if rating_span else "no_rating"

            # 更新时间选择器（使用title属性）
            time = (
                item.find("span", class_="comment-time")["title"]
                if item.find("span", class_="comment-time")
                else "未知时间"
            )

            comment_data = {
                "user": user,
                "rating": rating,
                "time": time,
                "content": comment_text,
            }
            self.comments.append(comment_data)
            print(f"获取评论: {comment_text[:50]}...")

    def closed(self, reason):
        # 爬虫结束时保存评论到文件
        with open(f"book_{self.book_id}_comments.json", "w", encoding="utf-8") as f:
            json.dump(self.comments, f, ensure_ascii=False, indent=2)
        print(f"共获取 {len(self.comments)} 条评论，已保存到文件。")


def run_spider(book_id):
    """运行爬虫的入口函数"""
    process = CrawlerProcess(
        {
            "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "ROBOTSTXT_OBEY": False,
            "CONCURRENT_REQUESTS": 1,  # 降低并发数，避免被封
            "DOWNLOAD_DELAY": 3,  # 下载延迟
            "COOKIES_ENABLED": False,
        }
    )

    process.crawl(DoubanBookSpider, book_id=book_id)
    process.start()


if __name__ == "__main__":
    book_id = "4913064"  # 这里是《活着》的ID
    run_spider(book_id)
