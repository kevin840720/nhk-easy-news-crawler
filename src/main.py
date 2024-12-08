# -*- encoding: utf-8 -*-
"""
@File    :  main.py
@Time    :  2024/02/06 13:44:39
@Author  :  Kevin Wang
@Desc    :  None
"""

from crawler import NHKEasyWebCrawler, NHKWebCrawler
from export import Export2PostgreSQL

if __name__ == "__main__":
    from datetime import datetime
    news_list = (NHKEasyWebCrawler().download_recent_news(start_date=datetime(2024, 12, 7))
                 + NHKWebCrawler().download_recent_news(start_date=datetime(2024, 12, 7))
                 )
    export_class = Export2PostgreSQL()
    for news in news_list:
        export_class.insert(news)
