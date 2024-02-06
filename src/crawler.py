# -*- encoding: utf-8 -*-
"""
@File    :  crawler.py
@Time    :  2024/02/06 15:59:36
@Author  :  Kevin Wang
@Desc    :  None
"""

from datetime import datetime, timedelta
from typing import Dict
import json

from objects import News
from utils import NHKEasyWebRequests


class NHKEasyWebCrawler:
    def __init__(self):
        self.crawler = NHKEasyWebRequests()

    def get_recent_news(self,
                        start_date:datetime=None,
                        end_date:datetime=None,
                        ):
        start_date = start_date if start_date else (datetime.now() - timedelta(days=365)).date()
        end_date = end_date if end_date else datetime.now().date()
        if start_date < (datetime.now() - timedelta(days=365)).date():
            raise ValueError("Start date cannot be more than one year ago.")
        
        def iterate_news_list(start_date, end_date) -> dict:
            news_list = json.loads(self.crawler.get_news_list().text)[0]
            for _date in news_list:
                date = datetime.strptime(_date, "%Y-%m-%d")
                # if 
                for news_info in news_list[_date]:
                    yield date
        
        for news in iterate_news_list(start_date, end_date):
            print(news)
        return self.crawler.get_news_list()
    
if __name__ == "__main__":
    print(NHKEasyWebCrawler().get_recent_news())