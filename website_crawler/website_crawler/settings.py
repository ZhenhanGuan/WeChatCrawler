BOT_NAME = "website_crawler"

SPIDER_MODULES = ["website_crawler.spiders"]
NEWSPIDER_MODULE = "website_xcrawler.spiders"

ROBOTSTXT_OBEY = False
DOWNLOAD_DELAY = 1  # 延迟，防止过快请求
CONCURRENT_REQUESTS = 8

DEFAULT_REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

# 如果只想导出 CSV，不需要启用 MongoDB
# 如果需要 MongoDB，取消注释下面这行
# ITEM_PIPELINES = {
#     "website_crawler.pipelines.MongoPipeline": 1,
# }
