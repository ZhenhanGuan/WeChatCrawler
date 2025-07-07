from playwright.sync_api import Playwright, sync_playwright, expect
import time
from datetime import datetime
import json, jsonlines
import os
# from keywords import keywords

keywords = ["机器之心", "上海科技大学", "PaperWeekly"]


def fake(page):
    page.mouse.wheel(0,1200)
    time.sleep(1)
    page.mouse.wheel(0,200)
    time.sleep(1)
    page.mouse.wheel(0,200)
    time.sleep(1)
    page.mouse.wheel(0,200)
    time.sleep(1)
    page.mouse.wheel(0,200)
    time.sleep(1)
    page.mouse.wheel(0,200)

file_path = "/Users/zhenhan_guan/Desktop/CodeBase/FinancialRAG/article_links.jsonl"

def init_dic():
    data = {}
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = json.loads(line)
                if data.get(line["pub_name"]) is None:
                    data[line["pub_name"]] = []
                data[line["pub_name"]].append(line["url"])
    return data
    
data = init_dic()

comparison_date = datetime.strptime("2025-07-02", "%Y-%m-%d")

# def get_links(page, pub_name):
#     time.sleep(5)
#      # 定位到所有的label元素
#     labels = page.locator('label.inner_link_article_item')

#     # 获取元素数量
#     count = labels.count()
#     print(f"当前页共有{count}篇文章")
#     if count == 0:
#         return False

#     # 遍历所有label元素
#     for i in range(count):
#         # 对于每个label元素，找到其下的第二个span中的a标签的href属性
#         href_value = labels.nth(i).locator('span:nth-of-type(2) a').get_attribute('href')
#         date_element_text = labels.nth(i).locator('.inner_link_article_date').text_content()
#         test_date = datetime.strptime(date_element_text, "%Y-%m-%d")
#         if test_date < comparison_date:
#             return None
#         if href_value not in data[pub_name]:
#             data[pub_name].append(href_value)
#             with jsonlines.open(file_path, mode='a') as writer:
#                 writer.write({"pub_name": pub_name, "url": href_value})
#             if len(data[pub_name]) >= 500:
#                 return None

#     return True

def get_links(page, pub_name):
    time.sleep(3)
    labels = page.locator('label.inner_link_article_item')
    count = labels.count()
    print(f"当前页共有 {count} 篇文章")

    if count == 0:
        return False

    for i in range(count):
        href_value = labels.nth(i).locator('span:nth-of-type(2) a').get_attribute('href')
        date_element_text = labels.nth(i).locator('.inner_link_article_date').text_content().strip()
        date_str = date_element_text[:10]

        try:
            test_date = datetime.strptime(date_str, "%Y-%m-%d")
        except Exception as e:
            print(f"解析日期失败: {date_str}, 跳过")
            continue

        print(f"文章日期: {test_date.date()}, 链接: {href_value}")

        if test_date < comparison_date:
            print("遇到早于限定日期的文章，停止抓取")
            return None

        if href_value not in data[pub_name]:
            data[pub_name].append(href_value)
            with jsonlines.open(file_path, mode='a') as writer:
                writer.write({"pubulish_date": str(test_date.date()), "pub_name": pub_name, "url": href_value })

        if len(data[pub_name]) >= 500:
            print("已抓够 500 篇文章，提前停止")
            return None

    return True


def login(playwright: Playwright):
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()    
    page.goto("https://mp.weixin.qq.com/")
    with page.expect_popup() as page1_info:
        page.locator(".new-creation__icon > svg").first.click(timeout=1000000)
    page1 = page1_info.value
    cookies = page.context.cookies()
    page1.close()
    page.close()
    context.close()
    browser.close()
    return cookies

def get_cookies():
    with sync_playwright() as playwright:
        cookies = login(playwright)
    return cookies

cookies = get_cookies()

def record_state(count_path, page_count):
    with open(count_path, 'w') as f:
        f.write(str(page_count - 1))


def run(playwright: Playwright, pub_name) -> None:    
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.context.add_cookies(cookies)
    page.goto("https://mp.weixin.qq.com/")

    with page.expect_popup() as page1_info:
        page.locator(".new-creation__icon > svg").first.click(timeout=1000000)
    page1 = page1_info.value
    
    # page1.get_by_text("超链接").click()

    page1.get_by_text("超链接").nth(0).wait_for(state="visible")
    page1.get_by_text("超链接").nth(0).click()

    page1.get_by_text("选择其他账号", exact=False).wait_for(state="visible", timeout=60000)
    page1.get_by_text("选择其他账号", exact=False).click()

    page1.get_by_placeholder("输入文章来源的账号名称或微信号，回车进行搜索").click()
    page1.get_by_placeholder("输入文章来源的账号名称或微信号，回车进行搜索").fill(pub_name)
    page1.get_by_placeholder("输入文章来源的账号名称或微信号，回车进行搜索").press("Enter")
    page1.get_by_text(f"{pub_name}", exact=False).nth(0).click()


    page_count = 0
    count_path = f"./tmp/page_count_{pub_name}.txt"
    # if os.path.exists(count_path):
    #     with open(count_path, 'r') as f:
    #         page_count = int(f.read())


    print("8888888888888page:", page_count)

    if page_count > 0:
        page1.fill('input[type="number"]', str(page_count))
        page1.get_by_role("link", name="跳转").click()
    
    error_flag = False
    this_count = 0

    while (True):
        page_count += 1
        this_count += 1
        if this_count > 10:
            print(12)
            record_state(count_path, page_count)
            error_flag = True
            break
        print(f"公众号 {pub_name} 第{page_count}页")
        flag = get_links(page1, pub_name)
        if flag is None:
            print(13)
            record_state(count_path, page_count)
            error_flag = None
            break
        
        if not flag:
            print(14)
            record_state(count_path, page_count)
            error_flag = True
            break
        fake(page1)
        next_button = page1.get_by_role("link", name="下一页")

        if (next_button.count() == 0):
            print(15)
            record_state(count_path, page_count)
            error_flag = True
            break
        print(f"此公众号总共获取到{len(data[pub_name])}篇文章")

        next_button.click()
        
    page1.close()
    page.close()
    context.close()
    browser.close()
    return error_flag

def check_folder():
    if not os.path.exists("tmp"):
        os.makedirs("tmp")

check_folder()

for keyword in keywords:
    if data.get(keyword) is None:
        data[keyword] = []
    with sync_playwright() as playwright:
        flag = run(playwright, keyword)
        if flag is None:
            continue
        if flag:
            break