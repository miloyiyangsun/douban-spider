import scrapy
from scrapy.crawler import CrawlerProcess
import random
import time
from bs4 import BeautifulSoup
import json
from urllib.parse import quote


class DoubanBookSpider(scrapy.Spider):
    name = "douban_book"
    allowed_domains = ["book.douban.com"]

    def __init__(self, book_id=None, *args, **kwargs):
        super(DoubanBookSpider, self).__init__(*args, **kwargs)
        self.book_id = book_id
        self.comments = []

    def start_requests(self):
        # 先通过搜索获取book_id（如果需要根据书名查找）
        search_url = (
            f"https://book.douban.com/j/subject_suggest?q={quote(self.book_name)}"
        )
        yield scrapy.Request(
            url=search_url,
            callback=self.parse_search,
            headers=self.get_random_headers(),
        )

    def parse_search(self, response):
        # 解析搜索结果的JSON获取准确book_id
        try:
            data = json.loads(response.text)
            if data:
                self.book_id = data[0]["id"]
                # 开始请求评论页
                for req in self.generate_comment_requests():
                    yield req
        except Exception as e:
            self.logger.error(f"搜索失败: {e}")

    def get_random_headers(self):
        # 使用你提供的UA列表
        user_agents = [...]  # 粘贴你提供的完整UA列表
        return {
            "User-Agent": random.choice(user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Host": "book.douban.com",
            "Referer": "https://book.douban.com/",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
        }

    def generate_comment_requests(self):
        # 生成评论页请求
        base_url = f"https://book.douban.com/subject/{self.book_id}/comments/"
        for page in range(5):
            yield scrapy.Request(
                url=f"{base_url}?start={page*20}",
                callback=self.parse_comments,
                headers=self.get_random_headers(),
                meta={"proxy": "http://your_proxy:port"},  # 如果需要代理
                errback=self.errback_handler,
            )

    def parse_comments(self, response):
        # 使用XPath选择器更可靠
        for item in response.xpath('//li[@class="comment-item"]'):
            # 使用更稳健的解析方式
            yield {
                "user": item.xpath('.//span[@class="comment-info"]/a/text()')
                .get(default="匿名用户")
                .strip(),
                "rating": item.xpath(
                    './/span[contains(@class,"rating")]/@class'
                ).re_first(r"allstar(\d+)")
                or "0",
                "time": item.xpath('.//span[@class="comment-time"]/@title').get(),
                "content": "".join(
                    item.xpath('.//span[@class="short"]/text()').getall()
                ).strip(),
            }

    def errback_handler(self, failure):
        # 处理请求失败
        self.logger.error(repr(failure))

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
            "CONCURRENT_REQUESTS": 2,  # 降低并发数，避免被封
            "DOWNLOAD_DELAY": 5,  # 下载延迟
            "COOKIES_ENABLED": False,
            "AUTOTHROTTLE_ENABLED": True,  # 启用自动限速
        }
    )

    process.crawl(DoubanBookSpider, book_id=book_id)
    process.start()


if __name__ == "__main__":
    book_id = "4913064"  # 这里是《活着》的ID
    run_spider(book_id)
