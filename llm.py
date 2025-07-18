#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from prompt import *
import os
import sys
import requests
import json
from typing import Literal
import base64
# -----------------------------
# 配置部分
# -----------------------------


class ReWriter():
    def __init__(self) -> None:
        self.api_key = "sk-8AR3SSNkATeUsIdDkZMTZ3Eow5UKXqtrxb7s2L0AiOVppMJ8"

# -----------------------------
# 核心函数：生成对话
# -----------------------------
    def chat_completion(self, user_input="", image_url_list=None, model="gpt-4o", temperature=0.7):
        """
        向 OpenAI 发送对话请求，并返回模型的回复内容。
        :param messages: list of dict, e.g. [{"role": "system", "content": "You are a helpful assistant."}, ...]
        :param model: 使用的模型名称
        :param temperature: 采样温度，值越高越发散
        :param max_tokens: 最大输出 token 数
        :return: 模型回复字符串
        """
        #模版选择


        

        #------------------------------
        #文本重写
        #------------------------------
        if model == "gpt-4o":
            run_times = 0
            max_run_times = 5
            print("++++++++🔄正在进行重写文本🔄++++++++")
            status = "failed"

            while(status=="failed" and run_times < max_run_times):
                run_times += 1
                print(f"🔄 尝试第 {run_times} 次")                
                api_url = "https://api2.aigcbest.top/v1/chat/completions"
                prompt =  TEXT_REWRITE_PROMPT

                messages = [
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": user_input}
                    ]

                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                }
                payload = {
                    "model": model,
                    "messages": messages,
                    # "temperature": temperature,
                    # "max_tokens": max_tokens,
                    # 如需开启流式输出，设置 "stream": True
                }

                try:
                    response = requests.post(api_url, headers=headers, json=payload, timeout=1000000)
                    response.raise_for_status()  # 若响应码不是 200，会抛出 HTTPError
                    status = "success"
                except requests.exceptions.RequestException as e:
                    status = "failed"
                    print(f"❌ 请求失败：{e}", file=sys.stderr)

                data = response.json()
                # 解析返回的消息
                try:
                    return data["choices"][0]["message"]["content"].strip()
                except (KeyError, IndexError) as e:
                    print("❌ 返回格式异常，无法解析：", data, file=sys.stderr)
                    return None

        #------------------------------
        #图片重写
        #------------------------------
        elif model == "dall-e-2":
            print("++++++++🔄正在进行重写图片🔄++++++++")
            api_url = "https://api2.aigcbest.top/v1/images/edits"
            prompt = IMAGE_REWRITE_PROMPT
            rewrite_image_url_list = []

            for url in image_url_list:
                run_times = 0
                max_run_times = 5
                status = "failed"
                while(status=="failed" and run_times < max_run_times):
                    run_times += 1
                    print(f"🔄 尝试第 {run_times} 次")
                    with open(url, "rb") as image_file:
                        # 可选：你可以上传一个透明区域作为掩码（mask.png），否则不需要该字段
                        # with open("mask.png", "rb") as mask_file:
                        files = {
                            "image": ("input.png", image_file, "image/png"),
                            # "mask": ("mask.png", mask_file, "image/png"),  # 可选
                        }

                        data = {
                            "prompt": prompt,
                            "model": model,
                            "n": 1,
                            "size": "1024x1024"
                        }

                        headers = {
                            "Authorization": f"Bearer {self.api_key}"
                        }

                        response = requests.post(api_url, headers=headers, files=files, data=data)

                        # 处理响应
                        if response.status_code == 200:
                            result = response.json()
                            b64_data = result["data"][0]["b64_json"]
                            num = len(rewrite_image_url_list)
                            rewrite_image = f"rewrite_image{num}.png"

                            with open(rewrite_image, "wb") as f:
                                f.write(base64.b64decode(b64_data))

                            raw_image_url_base = os.path.dirname(url)
                            rewrite_image_url = os.path.join(raw_image_url_base, rewrite_image)
                            rewrite_image_url_list.append(rewrite_image_url)
                            status = "success"
                            print(f"✅ 重写{num+1}/{len(image_url_list)}图片完成！已保存{rewrite_image},url:{rewrite_image_url}")
                        else:
                            status = "failed"
                            print(f"❌ 请求失败: {response.status_code}")
                            print(response.text)     

            return rewrite_image_url_list

    def rewrite():
        pass

if __name__ == "__main__":
    rewriter = ReWriter()
    # input = "常州天气"
    # response = rewriter.chat_completion(user_input=input, model="gpt-4o")
    # print(response)

    test_list = ["/Users/zhenhan_guan/Desktop/CodeBase/FinancialRAG/images/001.png",
                 "/Users/zhenhan_guan/Desktop/CodeBase/FinancialRAG/images/002.png",
                 "/Users/zhenhan_guan/Desktop/CodeBase/FinancialRAG/images/003.png"]
    result = rewriter.chat_completion(image_url_list=test_list, model="dall-e-2")
    print(result)
