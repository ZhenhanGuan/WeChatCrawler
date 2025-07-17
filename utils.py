import requests
from datetime import datetime, timedelta
import os

def upload_document(authorization_token, file_path_list: list, kb_name, kb_id, url, run=1, is_parse=True):
    doc_id_list = []

    #上传文件
    for file_path in file_path_list:
        url = url
        headers = {
            "Authorization": authorization_token
            # "Content-Type: multipart/form-data"
        }
        files = {
            "file": open(file_path, "rb")
        }
        data = {
            "kb_name": kb_name,
            "kb_id": kb_id,
            # "parser_id": "可选，指定解析器",
            "run": "1"  # 可选，立即解析
        }

        response = requests.post(url, headers=headers, files=files, data=data)
        doc_id = response.json()["data"][0]["id"]
        doc_id_list.append(doc_id)
    
    # 解析
    if is_parse:
        url = "http://127.0.0.1/v1/document/run"
        parse_document(authorization_token, kb_id, url, doc_id_list, run)
    

    try:
        data = response.json()
    except ValueError:
        print("Response is not JSON!")
        data = response.text
    print(data)



def parse_document(authorization_token, kb_id, url, doc_id_list: list, run=1):
    url = url
    headers = {
        "Authorization": authorization_token,
        "Content-Type": "application/json"
    }
    data = {
        "doc_ids": doc_id_list,
        "run": run,
        "kb_id": kb_id,

    }

    response = requests.post(url, headers=headers, json=data)

    try:
        data = response.json()
    except ValueError:
        print("Response is not JSON!")
        data = response.text
    print(data)

if __name__ == "__main__":
    
    authorization_token = "IjcwMTRlODgwNWJjNDExZjA4ZjAwM2U0ODRmOWZmZGE0Ig.aGy6Ag.AAqC3q8vv362lteVcZUHVqDVzkc"
    url = "http://127.0.0.1/v1/document/upload"
    
    file_path_list = ["/Users/zhenhan_guan/Desktop/CodeBase/FinancialRAG/wechat_article/机器之心/2025-07-03/08ea4e26-32ca-4dae-8e90-1a05a19cf4fa_article_content.md",
                      "/Users/zhenhan_guan/Desktop/CodeBase/FinancialRAG/wechat_article/机器之心/2025-07-03/213fdabc-2094-4893-a97e-9c804f37f8bc_article_content.md",
                        "/Users/zhenhan_guan/Desktop/CodeBase/FinancialRAG/wechat_article/机器之心/2025-07-03/a4531515-573c-4f87-a7dc-904e0f558315_article_content.md"]
    kb_id = "d0b23dea5bc511f0ad223e484f9ffda4"
    kb_name = "FinancialWechat"

    
    upload_document(authorization_token, file_path_list, kb_name, kb_id, url, is_parse=True)


def get_file_path_list(wechat_official_accounts, article_path, start_date_str):

    # start_data_str="2025-07-02"
    date_list = []
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    end_date = datetime.today().date()

    current_date = start_date
    while current_date <= end_date:
        # print(current_date)
        # current_date.strftime("%Y-%m-%d")
        # date_str_list = [d.strftime("%Y-%m-%d") for d in date_list]
        date_list.append(current_date.strftime("%Y-%m-%d"))
        current_date += timedelta(days=1) 

    metadata_path_list = []
    for account in wechat_official_accounts:
        account_path = article_path + account

        for date in date_list:
            # file_metadate_path = os.path.join(account_path,date,"metadata.jsonl")
            file_metadate_path = os.path.join(account_path,date)

            if os.path.exists(file_metadate_path):
                for filename in os.listdir(file_metadate_path):
                    metadata_path = os.path.join(file_metadate_path, filename)
                    if os.path.isfile(metadata_path) and filename != "metadata.jsonl":
                        # print("找到公众号文章:", metadata_path)
                        metadata_path_list.append(metadata_path)

                # print(len(metadata_path_list))
            else:
                print(f"未找到公众号“{account}”在“{date}”的文章,请确认公众号这天是否有文章！")
       
    return metadata_path_list