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


# ========================================
# 初始化元信息记录
# ========================================
article_link_path = "/Users/zhenhan_guan/Desktop/CodeBase/FinancialRAG/article_links.jsonl"
article_link_list = []
base_wechat_article_path = "/Users/zhenhan_guan/Desktop/CodeBase/FinancialRAG/wechat_article/"

with jsonlines.open(article_link_path, mode='r') as reader:
    # for obj in reader:
    #     print(obj)
    for obj in reader:
        article_link_list.append(obj)

for article_link in article_link_list:
    url = article_link["url"]
    # url = "https://mp.weixin.qq.com/s/KcaiK4PjN0FbFAyZifLogg"
    pub_name = article_link["pub_name"]
    pubulish_date = article_link["pubulish_date"]

    scrape_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "failed"
    error_message = ""
    image_urls = []
    video_urls = []
    title = ""
    markdown_content = ""
    run_times = 0
    max_run_times = 10
    # ========================================
    # 启动浏览器爬取内容
    # ========================================

    print(f"正在爬取@@ 日期:{pubulish_date},公众号:{pub_name},URL:{url}")

    while(status=="failed" and run_times < max_run_times):
        try:
            run_times += 1
            print(f"🔄 尝试第 {run_times} 次")
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")

            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            driver.get(url)
            html = driver.page_source
            driver.quit()

            soup = BeautifulSoup(html, "html.parser")

            # 获取标题
            title_tag = soup.find("h1")
            title = title_tag.get_text(strip=True) if title_tag else "Untitled"

            content_div = soup.find("div", class_="rich_media_content")
            if not content_div:
                raise Exception("未找到内容区域")

            markdown_lines = [f"# {title}\n"]

            # 遍历内容中的直接子节点，按顺序处理
            for child in content_div.contents:
                if isinstance(child, NavigableString):
                    text = child.strip()
                    if text:
                        markdown_lines.append(text + "\n")
                elif isinstance(child, Tag):
                    # 处理图片
                    if child.name == "img":
                        img_url = child.get("data-src")
                        if img_url:
                            image_urls.append(img_url)
                            markdown_lines.append(f"![]({img_url})\n")

                    # 处理视频 iframe
                    elif child.name == "iframe":
                        video_url = child.get("data-src")
                        if video_url:
                            video_urls.append(video_url)
                            markdown_lines.append(f"[视频链接]({video_url})\n")

                    else:
                        # 如果是段落标签或其他标签，递归提取里面的文字
                        text = child.get_text(strip=True)
                        if text:
                            markdown_lines.append(text + "\n")

                        # 同时处理标签内部的图片
                        img_tags = child.find_all("img")
                        for img_tag in img_tags:
                            img_url = img_tag.get("data-src")
                            if img_url:
                                image_urls.append(img_url)
                                markdown_lines.append(f"![]({img_url})\n")

                        # 同时处理标签内部的视频 iframe
                        iframe_tags = child.find_all("iframe")
                        for iframe_tag in iframe_tags:
                            video_url = iframe_tag.get("data-src")
                            if video_url:
                                video_urls.append(video_url)
                                markdown_lines.append(f"[视频链接]({video_url})\n")

            status = "success"
            error_message = ""

        except Exception as e:
            status = "failed"
            error_message = str(e)


        
    article_uuid = str(uuid.uuid4())
    
    article_path = base_wechat_article_path + f"{pub_name}/{pubulish_date}"
    if not os.path.exists(article_path):
        os.makedirs(article_path)

    metadata = {
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
        }

    # ========================================
    # 保存 markdown 文件
    # ========================================
    if status == "success":
        markdown_content = "\n".join(markdown_lines)
        with open(f"{article_path}/{article_uuid}_article_content.md", "w", encoding="utf-8") as f:
            f.write(markdown_content)

    # ========================================
    # 写入 JSON 文件
    # ========================================

    with open(f"{article_path}/metadata.json", "a", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=4)

        print(f"✅ 爬取完成，状态：{status}")


    if status == "success":
        print("已生成文件")
    else:
        print(f"错误信息：{error_message}")
