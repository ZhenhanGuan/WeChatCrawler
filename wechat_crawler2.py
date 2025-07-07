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



# ========================================
# 初始化元信息记录
# ========================================
url = "https://mp.weixin.qq.com/s/J8qtGMAZGxJwgi_TYeISFg"  # 替换成目标链接
scrape_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
status = "success"
error_message = ""
image_urls = []
video_urls = []
title = ""
markdown_content = ""


base_file_path = "/Users/zhenhan_guan/Desktop/CodeBase/FinancialRAG/wechat_article/"

if not os.path.exists(base_file_path):
    os.mkdir(base_file_path)

# ========================================
# 启动浏览器爬取内容
# ========================================
try:
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

except Exception as e:
    status = "failed"
    error_message = str(e)

    
article_uuid = str(uuid.uuid4())

# ========================================
# 保存 markdown 文件
# ========================================
if status == "success":
    markdown_content = "\n".join(markdown_lines)
    with open(f"{base_file_path}{scrape_time}_{article_uuid}_article_content.md", "w", encoding="utf-8") as f:
        f.write(markdown_content)

# ========================================
# 写入 JSON 文件
# ========================================


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

with open(f"{base_file_path}{scrape_time}_{article_uuid}_article_data.json", "w", encoding="utf-8") as f:
    json.dump(metadata, f, ensure_ascii=False, indent=4)

print(f"✅ 爬取完成，状态：{status}")
if status == "success":
    print("已生成文件：article_content.md 和 article_data.json")
else:
    print(f"错误信息：{error_message}")
