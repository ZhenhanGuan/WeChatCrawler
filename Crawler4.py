import time
import csv
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# ============ Selenium 配置 ============
options = Options()
# options.add_argument("--headless")  # 需要扫码的话先注释
options.add_argument("--disable-gpu")
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

# ============ 公众号主页 URL ============
homepage_url = "https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=XXXXXX..."  # 替换成你自己的

driver.get(homepage_url)
print("请扫码登录，如需要。等待 20 秒加载历史文章...")
time.sleep(20)

# ============ 滑动加载几次（只需要最近几条即可） ============
for _ in range(3):
    driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
    time.sleep(2)

# ============ 提取文章链接及发布时间 ============
articles = driver.find_elements(By.CSS_SELECTOR, "div.weui_media_box")

today_str = datetime.datetime.now().strftime("%Y-%m-%d")

article_urls = []

for article in articles:
    try:
        # 提取发布时间（格式：YYYY-MM-DD）
        time_elem = article.find_element(By.CLASS_NAME, "weui_media_extra_info")
        publish_time = time_elem.text.strip()

        # 判断是否为今天
        if today_str not in publish_time:
            continue

        # 提取文章链接
        link_elem = article.find_element(By.CSS_SELECTOR, "a.weui_media_title")
        article_url = link_elem.get_attribute("hrefs") or link_elem.get_attribute("href")
        article_urls.append(article_url)

    except Exception as e:
        print("解析文章失败：", e)

print(f"找到当天文章共 {len(article_urls)} 篇")

# ============ CSV 文件保存 ============
csv_file = open("wechat_today_articles.csv", "w", encoding="utf-8-sig", newline="")
writer = csv.writer(csv_file)
writer.writerow(["文章标题", "公众号名称", "发布时间", "文章链接", "图片链接", "视频链接"])

# ============ 逐篇访问文章 ============
for idx, url in enumerate(article_urls):
    driver.get(url)
    time.sleep(2)

    # 公众号名称
    try:
        account_name = driver.find_element(By.ID, "js_name").text.strip()
    except:
        account_name = "未找到公众号名称"

    # 发布时间
    try:
        publish_time = driver.find_element(By.ID, "publish_time").text.strip()
    except:
        publish_time = today_str

    # 标题
    try:
        title = driver.find_element(By.TAG_NAME, "h1").text.strip()
    except:
        title = "未找到标题"

    # 图片
    imgs = driver.find_elements(By.CSS_SELECTOR, "img")
    img_links = [img.get_attribute("data-src") or img.get_attribute("src") for img in imgs if (img.get_attribute("data-src") or img.get_attribute("src"))]
    img_str = ",".join(img_links)

    # 视频
    videos = driver.find_elements(By.TAG_NAME, "iframe")
    video_links = [v.get_attribute("data-src") or v.get_attribute("src") for v in videos if (v.get_attribute("data-src") or v.get_attribute("src"))]
    video_str = ",".join(video_links)

    # 写入 CSV
    writer.writerow([title, account_name, publish_time, url, img_str, video_str])

    print(f"完成第 {idx+1}/{len(article_urls)} 篇：{title}")

csv_file.close()
driver.quit()

print("✅ 当天文章已提取完成，结果保存到 wechat_today_articles.csv")
