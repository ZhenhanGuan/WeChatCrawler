import os
import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup, NavigableString, Tag
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import uuid
import jsonlines


file_path = "/Users/zhenhan_guan/Desktop/CodeBase/FinancialRAG/article_links.jsonl"
with jsonlines.open(file_path, mode='r') as reader:
    # for obj in reader:
    #     print(obj)

    for obj in reader:
        print(obj["url"])