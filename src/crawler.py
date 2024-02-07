# -*- encoding: utf-8 -*-
"""
@File    :  crawler.py
@Time    :  2024/02/06 15:59:36
@Author  :  Kevin Wang
@Desc    :  None
"""

from datetime import datetime, timedelta
from typing import Dict
from pathlib import Path
import json

from bs4 import BeautifulSoup

from config import ProjectConfigs
from objects import Content, News, Voice
from utils import NHKEasyWebRequests

class NHKEasyWebCrawler:
    def __init__(self):
        self.crawler = NHKEasyWebRequests()
        self._news = []

    def download_voice(self,
                       voice_id:str,
                       voice_dir=ProjectConfigs.RAW_DIR.joinpath("nhk_easy_web/voices"),
                       ) -> Voice:
        """This function is going to handle the response object.

        Args:
            voice_id (str): _description_
            voice_dir (_type_, optional): _description_. Defaults to ProjectConfigs.RAW_DIR.joinpath("nhk_easy_web/voices").

        Returns:
            Path: _description_
        """
        response = self.crawler.get_voice(voice_id)
        path = voice_dir.joinpath(f'{voice_id}.m3u8')
        if response.status_code == 200:
            with open(path, 'wb') as file:
                file.write(response.content)
        return Voice(response.status_code,
                     voice_id,
                     response.url,
                     None,
                     datetime.now(),
                     path,
                     )

    def download_content(self,
                         content_id:str,
                         content_dir=ProjectConfigs.RAW_DIR.joinpath("nhk_easy_web/contents"),
                         ) -> Content:
        response = self.crawler.get_easy_content(content_id)
        path = content_dir.joinpath(f'{content_id}.html')
        soup = BeautifulSoup(response.text, 'html.parser')
        if response.status_code == 200:
            with open(path, 'wb') as file:
                file.write(response.content)
        return Content(response.status_code,
                       content_id,
                       response.url,
                       None,
                       datetime.now(),
                       path,
                       # soup,
                       )

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
                date = datetime.strptime(_date, "%Y-%m-%d").date()
                if date < start_date or date > end_date:
                    continue
                for news_info in news_list[_date]:
                    yield news_info
        
        news = []
        for news_info in iterate_news_list(start_date, end_date):
            publication_time = (news_info["news_publication_time"]
                                or news_info["news_preview_time"]
                                or news_info["news_creation_time"]
                                or news_info["news_prearranged_time"]
                                )
            publication_time = datetime.strptime(publication_time, "%Y-%m-%d %H:%M:%S")
            voice_id = news_info["news_easy_voice_uri"].split(".")[0]
            content = self.download_content(news_info["news_id"])
            voice = self.download_voice(voice_id)


            news.append(News("NHK Easy Web",
                             news_info["news_id"],
                             news_info["title"],
                             content.url,
                             publication_time,
                             datetime.now(),
                             None,
                             voice,
                             content,
                             )
                        )
        self._news += news
        return news
    
if __name__ == "__main__":
    a = NHKEasyWebCrawler().get_recent_news()
    # a = NHKEasyWebCrawler().download_voice("k10014346261000_6mHAVGzMvPy7augGieIgIWnP8lt6zVMdzJEAxJdk")
    # print(a)