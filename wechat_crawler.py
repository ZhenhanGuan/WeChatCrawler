import os
import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup, NavigableString, Tag
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import uuid
import jsonlines
from utils import download_images

class WeChatArticleContentCrawler:
    def __init__(self, base_wechat_article_path):
        self.base_wechat_article_path = base_wechat_article_path
        self.article_link_path = os.path.join(self.base_wechat_article_path, "article_links.jsonl")
        self.article_link_list = self._load_article_links()

    def _load_article_links(self):
        article_link_list = []
        if not os.path.exists(self.base_wechat_article_path):
            os.makedirs(self.base_wechat_article_path) 
        with jsonlines.open(self.article_link_path, mode='r') as reader:
            for obj in reader:
                article_link_list.append(obj)
        return article_link_list

    def _scrape_article(self, url):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.get(url)
        html = driver.page_source
        driver.quit()
        return html

    def _parse_article(self, html):
        soup = BeautifulSoup(html, "html.parser")
        title_tag = soup.find("h1")
        title = title_tag.get_text(strip=True) if title_tag else "Untitled"
        content_div = soup.find("div", class_="rich_media_content")
        if not content_div:
            raise Exception("未找到内容区域")
        markdown_lines = [f"# {title}\n"]
        image_urls = []
        video_urls = []
        text_lines = []
        for child in content_div.contents:
            if isinstance(child, NavigableString):
                text = child.strip()
                if text:
                    markdown_lines.append(text + "\n")
                    text_lines.append(text + "\n")
            elif isinstance(child, Tag):
                if child.name == "img":
                    img_url = child.get("data-src")
                    if img_url:
                        image_urls.append(img_url)
                        markdown_lines.append(f"![]({img_url})\n")
                elif child.name == "iframe":
                    video_url = child.get("data-src")
                    if video_url:
                        video_urls.append(video_url)
                        markdown_lines.append(f"[视频链接]({video_url})\n")
                else:
                    text = child.get_text(strip=True)
                    if text:
                        markdown_lines.append(text + "\n")
                        text_lines.append(text + "\n")
                    img_tags = child.find_all("img")
                    for img_tag in img_tags:
                        img_url = img_tag.get("data-src")
                        if img_url:
                            image_urls.append(img_url)
                            markdown_lines.append(f"![]({img_url})\n")
                    iframe_tags = child.find_all("iframe")
                    for iframe_tag in iframe_tags:
                        video_url = iframe_tag.get("data-src")
                        if video_url:
                            video_urls.append(video_url)
                            markdown_lines.append(f"[视频链接]({video_url})\n")
            
        return title, markdown_lines, image_urls, video_urls, text_lines

    def _save_article(self, index, markdown_lines, metadata):
        # article_path = os.path.join(self.base_wechat_article_path, pub_name)
        # if not os.path.exists(self.base_wechat_article_path):
        #     os.makedirs(self.base_wechat_article_path)
        markdown_content = "\n".join(markdown_lines)
        file_dir_path = os.path.join(self.base_wechat_article_path, str(index))
        if not os.path.exists(file_dir_path):
            os.makedirs(file_dir_path)

        article_url = os.path.join(file_dir_path, "raw_article_content.md")
        with open(article_url, "w", encoding="utf-8") as f:
            f.write(markdown_content)
            
        with jsonlines.open(f"{self.base_wechat_article_path}/article_metadata.jsonl", "a") as writer:
            # json.dump(metadata, f, ensure_ascii=False, indent=4)
            writer.write(metadata)

    def crawl_content_from_url(self):
        index = 0
        for article_link in self.article_link_list:
            url = article_link["url"]
            pub_name = article_link["pub_name"]
            pubulish_date = article_link["pubulish_date"]
            scrape_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            status = "failed"
            error_message = ""
            image_urls = []
            video_urls = []
            title = ""
            markdown_lines = []
            run_times = 0
            max_run_times = 10
            print(f"正在爬取@@ 日期:{pubulish_date},公众号:{pub_name},URL:{url}")
            while(status=="failed" and run_times < max_run_times):
                try:
                    run_times += 1
                    print(f"🔄 尝试第 {run_times} 次")
                    html = self._scrape_article(url)
                    title, markdown_lines, image_urls, video_urls, text_lines = self._parse_article(html)
                    status = "success"
                    error_message = ""
                except Exception as e:
                    status = "failed"
                    error_message = str(e)
            article_uuid = str(uuid.uuid4())
            metadata = {
                "index": index,
                "uuid" : article_uuid,
                "url": url,
                "scraped_at": scrape_time,
                "status": status,
                "error_message": error_message,
                "title": title,
                "image_urls": list(set(image_urls)),
                "video_urls": list(set(video_urls)),
                "image_count": len(set(image_urls)),
                "video_count": len(set(video_urls)),
                "text_lines": text_lines
            }

            
            if status == "success":
                self._save_article(index, markdown_lines, metadata)
                index += 1
                print(f"✅ 爬取完成，状态：{status}")
                print("已生成文章md文件")
                print("已生成元数据json文件")
            else:
                print(f"❌ 爬取失败，错误信息：{error_message}")

# 主流程入口
if __name__ == "__main__":
    base_wechat_article_path = "/Users/zhenhan_guan/Desktop/CodeBase/FinancialRAG/wechat_article/"
    crawler = WeChatArticleContentCrawler(base_wechat_article_path)
    crawler.crawl_content_from_url()
