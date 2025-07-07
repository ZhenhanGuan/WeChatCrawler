from playwright.sync_api import Playwright, sync_playwright, expect
import time
from datetime import datetime
import json, jsonlines
import os
class WeChatArticleUrlCrawler:
    def __init__(self, keywords=None, article_path=None, comparison_date_str="2025-07-02"):
        self.keywords = keywords 
        self.article_path = article_path
        self.file_path = os.path.join(self.article_path, "article_links.jsonl") 
        print(self.file_path)
        # self.file_path = "/Users/zhenhan_guan/Desktop/CodeBase/FinancialRAG/article_links.jsonl"
        self.comparison_date = datetime.strptime(comparison_date_str, "%Y-%m-%d")
        self.data = self.init_dic()
        self.cookies = self.get_cookies()
        self.check_folder()

    def fake(self, page):
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

    def init_dic(self):
        data = {}
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = json.loads(line)
                    if data.get(line["pub_name"]) is None:
                        data[line["pub_name"]] = []
                    data[line["pub_name"]].append(line["url"])
        return data

    def get_links(self, page, pub_name):
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

            if test_date < self.comparison_date:
                print("遇到早于限定日期的文章，停止抓取")
                return None

            if href_value not in self.data[pub_name]:
                self.data[pub_name].append(href_value)
                with jsonlines.open(self.file_path, mode='a') as writer:
                    writer.write({"pubulish_date": str(test_date.date()), "pub_name": pub_name, "url": href_value })

            if len(self.data[pub_name]) >= 500:
                print("已抓够 500 篇文章，提前停止")
                return None

        return True

    def login(self, playwright: Playwright):
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

    def get_cookies(self):
        with sync_playwright() as playwright:
            cookies = self.login(playwright)
        return cookies

    def record_state(self, count_path, page_count):
        with open(count_path, 'w') as f:
            f.write(str(page_count - 1))

    def run(self, playwright: Playwright, pub_name) -> None:    
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.context.add_cookies(self.cookies)
        page.goto("https://mp.weixin.qq.com/")

        with page.expect_popup() as page1_info:
            page.locator(".new-creation__icon > svg").first.click(timeout=1000000)
        page1 = page1_info.value
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

        if page_count > 0:
            page1.fill('input[type="number"]', str(page_count))
            page1.get_by_role("link", name="跳转").click()
        error_flag = False
        this_count = 0
        while (True):
            page_count += 1
            this_count += 1
            if this_count > 10:
                self.record_state(count_path, page_count)
                error_flag = True
                break
            print(f"公众号 {pub_name} 第{page_count}页")
            flag = self.get_links(page1, pub_name)
            if flag is None:
                self.record_state(count_path, page_count)
                error_flag = None
                break
            if not flag:
                self.record_state(count_path, page_count)
                error_flag = True
                break
            self.fake(page1)
            next_button = page1.get_by_role("link", name="下一页")
            if (next_button.count() == 0):
                self.record_state(count_path, page_count)
                error_flag = True
                break
            print(f"此公众号总共获取到{len(self.data[pub_name])}篇文章")
            next_button.click()
        page1.close()
        page.close()
        context.close()
        browser.close()
        return error_flag

    def check_folder(self):
        if not os.path.exists("tmp"):
            os.makedirs("tmp")

        if not os.path.exists(self.article_path):
            os.makedirs(self.article_path)

    def get_url_from_wechat(self):
        for keyword in self.keywords:
            if self.data.get(keyword) is None:
                self.data[keyword] = []
            with sync_playwright() as playwright:
                flag = self.run(playwright, keyword)
                if flag is None:
                    continue
                if flag:
                    break

# 下面是主流程入口
if __name__ == "__main__":
    keywords=["机器之心", "上海科技大学", "PaperWeekly"]
    file_path="/Users/zhenhan_guan/Desktop/CodeBase/FinancialRAG/article_links.jsonl"
    comparison_date_str="2025-07-02"
    crawler = WeChatArticleUrlCrawler(keywords=keywords, file_path=file_path, comparison_date_str=comparison_date_str)
    crawler.get_url_from_wechat()
