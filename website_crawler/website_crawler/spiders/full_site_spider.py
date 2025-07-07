import scrapy
import json

class WeixinArticleSpider(scrapy.Spider):
    name = "weixin_article"
    allowed_domains = ['mp.weixin.qq.com']
    start_urls = ['https://mp.weixin.qq.com/s/J8qtGMAZGxJwgi_TYeISFg']

    def parse(self, response):
        title = response.xpath('normalize-space(//h1[@class="rich_media_title" and @id="activity-name"])').get(default='')
        meta_description = response.xpath('//meta[@name="description"]/@content').get(default='').strip()

        # 正文
        texts = response.xpath('//div[@id="js_content"]//text()').getall()
        visible_text = ' '.join([t.strip() for t in texts if t.strip()])

        # 图片
        image_urls = response.xpath('//div[@id="js_content"]//img/@data-src | //div[@id="js_content"]//img/@src').getall()

        # 视频
        video_iframes = response.xpath('//iframe/@data-src | //iframe/@src').getall()

        # 作者（公众号名称）
        author = response.xpath('normalize-space(//a[contains(@class, "rich_media_meta_nickname")])').get(default='')

        # 发布时间
        publish_time = response.xpath('normalize-space(//span[@id="publish_time"])').get(default='')

        # 公众号微信号（一般为空）
        official_account_id = ''

        self.article_data = {
            'url': response.url,
            'title': title,
            'meta_description': meta_description,
            'author': author,
            'publish_time': publish_time,
            'official_account_id': official_account_id,
            'all_text': visible_text,
            'images': image_urls,
            'videos': video_iframes,
        }

    def closed(self, reason):
        if hasattr(self, 'article_data'):
            with open('output1.json', 'w', encoding='utf-8') as f:
                json.dump(self.article_data, f, ensure_ascii=False, indent=2)
