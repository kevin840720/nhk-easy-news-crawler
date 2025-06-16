# -*- encoding: utf-8 -*-
"""
@File    :  main.py
@Time    :  2024/02/06 13:44:39
@Author  :  Kevin Wang
@Desc    :  None
"""

from datetime import datetime
from typing import List, Optional

from crawler import NHKEasyWebCrawler, NHKWebCrawler
from export import Export2PostgreSQL

def run_nhk_easy_crawler(start_date:Optional[str]=None,
                         end_date:Optional[str]=None,
                         ) -> List[dict]:
    """
    Run the NHK Easy News crawler and insert news into the database.

    Args:
        start_date (Optional[str]): Start date in 'YYYY-MM-DD' format. Defaults to None.
        end_date (Optional[str]): End date in 'YYYY-MM-DD' format. Defaults to None.

    Returns:
        int: Number of news items inserted.
    """
    if start_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
    if end_date:
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
    crawler = NHKEasyWebCrawler()
    exporter = Export2PostgreSQL()
    news_list = crawler.download_recent_news(start_date=start_date, end_date=end_date)
    for news in news_list:
        exporter.insert(news)
    return [news.to_json_dict() for news in news_list]

def run_nhk_crawler(start_date:Optional[str]=None,
                    end_date:Optional[str]=None,
                    ) -> List[dict]:
    """
    Run the NHK News crawler and insert news into the database.

    Args:
        start_date (Optional[str]): Start date in 'YYYY-MM-DD' format. Defaults to None.
        end_date (Optional[str]): End date in 'YYYY-MM-DD' format. Defaults to None.

    Returns:
        int: Number of news items inserted.
    """
    if start_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
    if end_date:
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
    crawler = NHKWebCrawler()
    exporter = Export2PostgreSQL()
    news_list = crawler.download_recent_news(start_date=start_date, end_date=end_date)
    for news in news_list:
        exporter.insert(news)
    return [news.to_json_dict() for news in news_list]

def run_nhk_crawler_all(start_date:Optional[str]=None,
                        end_date:Optional[str]=None
                        ) -> List[dict]:
    """
    Run both NHK Easy and NHK News crawlers and insert news into the database.

    Args:
        start_date (Optional[str]): Start date in 'YYYY-MM-DD' format. Defaults to None.
        end_date (Optional[str]): End date in 'YYYY-MM-DD' format. Defaults to None.

    Returns:
        List[dict]: List of news items as JSON dicts.
    """
    if start_date:
        start_date_dt = datetime.strptime(start_date, "%Y-%m-%d")
    else:
        start_date_dt = None
    if end_date:
        end_date_dt = datetime.strptime(end_date, "%Y-%m-%d")
    else:
        end_date_dt = None

    exporter = Export2PostgreSQL()
    news_list = (
        NHKEasyWebCrawler().download_recent_news(start_date=start_date_dt, end_date=end_date_dt) +
        NHKWebCrawler().download_recent_news(start_date=start_date_dt, end_date=end_date_dt)
    )
    for news in news_list:
        exporter.insert(news)
    return [news.to_json_dict() for news in news_list]

if __name__ == "__main__":
    print("NHK Easy:", run_nhk_easy_crawler())
    print("NHK:", run_nhk_crawler())
