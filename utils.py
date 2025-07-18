import requests
from datetime import datetime, timedelta
import os


import requests
import os

def download_images(url_list, output_dir="images"):
    os.makedirs(output_dir, exist_ok=True)

    for idx, url in enumerate(url_list, start=1):
        try:
            response = requests.get(url, stream=True, timeout=10)
            response.raise_for_status()

            # 自动判断扩展名（默认为 .jpg）
            # ext = os.path.splitext(url.split("?")[0])[1]
            # if ext.lower() not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            #     ext = '.png'

            ext = ".png"
            filename = f"{idx:03d}{ext}" 
            save_path = os.path.join(output_dir, filename)

            with open(save_path, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)

            print(f"✅ [{idx}] 下载成功: {save_path}")

        except Exception as e:
            print(f"❌ [{idx}] 下载失败: {url} | 原因: {e}")

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

# 示例用法
if __name__ == "__main__":
    url_list = [
        "https://mmbiz.qpic.cn/sz_mmbiz_png/KmXPKA19gWibb9end79VK2aSOBYuTvo2WvvNDE2uh245ua5QYbdDaODiaxhw83WkNYdkFQp0moDXGUaS4QxFicfew/640?wx_fmt=png&from=appmsg",
        "https://mmbiz.qpic.cn/sz_mmbiz_png/KmXPKA19gWibb9end79VK2aSOBYuTvo2WvvNDE2uh245ua5QYbdDaODiaxhw83WkNYdkFQp0moDXGUaS4QxFicfew/640?wx_fmt=png&from=appmsg",
        "https://mmbiz.qpic.cn/sz_mmbiz_png/KmXPKA19gWibb9end79VK2aSOBYuTvo2WvvNDE2uh245ua5QYbdDaODiaxhw83WkNYdkFQp0moDXGUaS4QxFicfew/640?wx_fmt=png&from=appmsg"
    ]

    download_images(url_list)


