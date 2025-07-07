import scrapy

class WebsiteCrawlerItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    meta_description = scrapy.Field()
    meta_keywords = scrapy.Field()
    all_text = scrapy.Field()
    images = scrapy.Field()
    videos = scrapy.Field()
