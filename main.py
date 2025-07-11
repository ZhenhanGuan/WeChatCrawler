from extarct_url import WeChatArticleUrlCrawler
from wechat_crawler import WeChatArticleContentCrawler
from utils import upload_document,get_file_path_list
from datetime import datetime, timedelta
import os

class WeChatArticleCrawler():
    pass


if __name__ == "__main__": 
    wechat_official_accounts=["中金所发布", "上交所发布", "李迅雷金融与投资", "量子位", "机器之心", "证券时报", "财经早餐"]
    article_path="/Users/zhenhan_guan/Desktop/CodeBase/FinancialRAG/wechat_article/"
    start_date_str="2025-07-08"

    #获取每个公众号的每个URL
    crawler1 = WeChatArticleUrlCrawler(wechat_official_accounts=wechat_official_accounts, article_path=article_path, start_date_str=start_date_str)
    crawler1.get_url_from_wechat()

    # #从每一个文章的URL获取文章内容和元数据
    crawler2 = WeChatArticleContentCrawler(article_path)
    crawler2.crawl_content_from_url()

    authorization_token = "IjcwMTRlODgwNWJjNDExZjA4ZjAwM2U0ODRmOWZmZGE0Ig.aGy6Ag.AAqC3q8vv362lteVcZUHVqDVzkc"
    url = "http://127.0.0.1/v1/document/upload"

    # path_list = get_file_path_list(wechat_official_accounts,article_path,start_date_str)
    # file_path_list = ["/Users/zhenhan_guan/Desktop/CodeBase/FinancialRAG/wechat_article/机器之心/2025-07-03/08ea4e26-32ca-4dae-8e90-1a05a19cf4fa_article_content.md",
    #                   "/Users/zhenhan_guan/Desktop/CodeBase/FinancialRAG/wechat_article/机器之心/2025-07-03/213fdabc-2094-4893-a97e-9c804f37f8bc_article_content.md",
    #                     "/Users/zhenhan_guan/Desktop/CodeBase/FinancialRAG/wechat_article/机器之心/2025-07-03/a4531515-573c-4f87-a7dc-904e0f558315_article_content.md"]
    
    kb_id = "d0b23dea5bc511f0ad223e484f9ffda4"
    kb_name = "FinancialWechat"

    
    # upload_document(authorization_token, path_list, kb_name, kb_id, url, is_parse=True)