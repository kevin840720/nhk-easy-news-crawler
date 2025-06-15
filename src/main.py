# -*- encoding: utf-8 -*-
"""
@File    :  main.py
@Time    :  2024/02/06 13:44:39
@Author  :  Kevin Wang
@Desc    :  None
"""

from datetime import datetime

from crawler import NHKEasyWebCrawler, NHKWebCrawler
from export import Export2PostgreSQL

def run_crawler(start_date=None, end_date=None):
    # 解析日期字串
    if start_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
    if end_date:
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
    news_list = (NHKEasyWebCrawler().download_recent_news(start_date=start_date, end_date=end_date)
                 + NHKWebCrawler().download_recent_news(start_date=start_date, end_date=end_date)
                 )
    export_class = Export2PostgreSQL()
    for news in news_list:
        export_class.insert(news)
    return len(news_list)

if __name__ == "__main__":
    run_crawler()