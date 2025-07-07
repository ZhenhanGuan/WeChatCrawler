from extarct_url import WeChatArticleUrlCrawler
from wechat_crawler import WeChatArticleContentCrawler

class WeChatArticleCrawler():
    pass



if __name__ == "__main__": 
    keywords=["机器之心", "上海科技大学", "PaperWeekly"]
    article_path="/Users/zhenhan_guan/Desktop/CodeBase/FinancialRAG/wechat_article/"
    comparison_date_str="2025-07-02"

    #获取每个公众号的每个URL
    crawler1 = WeChatArticleUrlCrawler(keywords=keywords, article_path=article_path, comparison_date_str=comparison_date_str)
    crawler1.get_url_from_wechat()

    #从每一个文章的URL获取文章内容和元数据
    crawler2 = WeChatArticleContentCrawler(article_path)
    crawler2.crawl_content_from_url()