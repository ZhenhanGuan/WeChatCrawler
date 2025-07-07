import os
import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# ========================================
# 初始化元信息记录
# ========================================
# url = "https://mp.weixin.qq.com/s/E1D_QA5lXwXRc6aSaU_zog"
url = "https://mp.weixin.qq.com/s/J8qtGMAZGxJwgi_TYeISFg"  # 替换成目标链接
scrape_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
status = "success"
error_message = ""
image_urls = []
video_urls = []
title = ""
content_text = ""

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

    # 获取标题和正文
    title = soup.find("h1").get_text(strip=True)
    content_div = soup.find("div", class_="rich_media_content")
    content_text = content_div.get_text(separator="\n", strip=True)

    # 提取图片链接
    img_tags = content_div.find_all("img")
    image_urls = [img.get("data-src") for img in img_tags if img.get("data-src")]

    print("@@@@@@@@@")
    print(image_urls)


    if not os.path.exists("images"):
        os.makedirs("images")

    for idx, img_url in enumerate(image_urls):
        try:

            img_data = requests.get(img_url).content
            print("*****************")
            with open(f"images/image_{idx+1}.jpg", "wb") as f:
                f.write(img_data)
        except Exception as e:
            print(f"图片下载失败：{img_url}，原因：{e}")

    # 提取视频链接
    iframe_tags = content_div.find_all("iframe")
    video_urls = [iframe.get("data-src") for iframe in iframe_tags if iframe.get("data-src")]

except Exception as e:
    status = "failed"
    error_message = str(e)

# ========================================
# 写入 JSON 文件
# ========================================
data = {
    "url": url,
    "scraped_at": scrape_time,
    "status": status,
    "error_message": error_message,
    "title": title,
    "content": content_text,
    "image_urls": image_urls,
    "video_urls": video_urls,
    "image_count": len(image_urls),
    "video_count": len(video_urls),
}

with open("article_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

# 同时写入 txt 文件
if status == "success":
    with open("article_content.txt", "w", encoding="utf-8") as f:
        f.write(f"标题：{title}\n\n")
        f.write(content_text)

print(f"✅ 数据已保存，状态：{status}")
