# -*- encoding: utf-8 -*-
"""
@File    :  crawler.py
@Time    :  2024/02/06 15:59:36
@Author  :  Kevin Wang
@Desc    :  None
"""

from datetime import datetime, timedelta
import json

from bs4 import BeautifulSoup

from config import ProjectConfigs
from objects import (Content,
                     News,
                     Voice,
                     )
from parser import NHKEasyNewsWebParser
from utils import (HLSMediaDownloader,
                   NHKEasyNewsClient,
                   )

class NHKEasyWebCrawler:
    """A web crawler for NHK Easy News, designed to download news content and associated audio.

    This class provides methods to retrieve recent news articles from NHK Easy Web, 
    downloading both the HTML content and voice recordings for each news item within 
    a specified date range.

    Example:
        crawler = NHKEasyWebCrawler()
        # Get news from the last 30 days
        recent_news = crawler.download_recent_news(
            start_date=datetime.now() - timedelta(days=30)
        )
    """
    def __init__(self):
        self.crawler = NHKEasyNewsClient()
        self._news = []

    def download_voice(self,
                       voice_id:str,
                       voice_dir=ProjectConfigs.RAW_DIR.joinpath("nhk_easy_web/voices"),
                       ) -> Voice:
        """Download an audio voice recording for a specific news item.

        Args:
            voice_id (str): Unique identifier for the voice recording.
            voice_dir (Path, optional): Directory to save the voice file. 
                Defaults to a predefined path in project configurations.

        Returns:
            Voice: An object representing the downloaded voice recording, 
                   containing metadata and file path.
        """
        response = self.crawler.get_voice_m3u8(voice_id)
        path = voice_dir.joinpath(f'{voice_id}.mp3')
        HLSMediaDownloader().save(response.url, path)
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
        """Download the HTML content for a specific news article.

        Args:
            content_id (str): Unique identifier for the news article.
            content_dir (Path, optional): Directory to save the HTML content. 
                Defaults to a predefined path in project configurations.

        Returns:
            Content: An object representing the downloaded content, 
                     containing metadata and file path.
        """
        response = self.crawler.get_content(content_id)
        path = content_dir.joinpath(f'{content_id}.html')
        soup = BeautifulSoup(response.content, 'html.parser')
        parser = NHKEasyNewsWebParser(soup)

        if response.status_code == 200:
            with open(path, 'wb') as file:
                file.write(response.content)
        try:
            publication_time = datetime.strptime(parser.date, "%Y年%m月%d日 %H時%M分")
        except ValueError:
            publication_time = None
        return Content(status=response.status_code,
                       id=content_id,
                       url=response.url,
                       title=parser.title,
                       article=parser.body,
                       publication_time=publication_time,
                       download_time=datetime.now(),
                       location=path,
                       html=response.text,
                       )

    def download_recent_news(self,
                             start_date:datetime=None,
                             end_date:datetime=None,
                             save_dir=ProjectConfigs.RAW_DIR.joinpath("nhk_easy_web"),
                             ):
        """Retrieve recent news articles within a specified date range.

        This method fetches news articles from NHK Easy Web, downloading both 
        content and voice recordings for each article. By default, it retrieves 
        news from the past year.

        Args:
            start_date (datetime, optional): The earliest date to retrieve news from. 
                Defaults to one year ago from the current date.
            end_date (datetime, optional): The latest date to retrieve news to. 
                Defaults to the current date.

        Returns:
            List[News]: A list of News objects containing article details, 
                        content, and voice recordings.

        Raises:
            ValueError: If the start date is more than one year in the past.
        """
        start_date = start_date if start_date else (datetime.now() - timedelta(days=365)).date()
        end_date = end_date if end_date else datetime.now().date()
        if start_date < (datetime.now() - timedelta(days=365)).date():
            raise ValueError("Start date cannot be more than one year ago.")

        def iterate_news_list(start_date, end_date) -> dict:
            news_list = self.crawler.get_news_summary()
            for _date in news_list:
                date = datetime.strptime(_date, "%Y-%m-%d").date()
                if date < start_date or date > end_date:
                    continue
                yield from news_list[_date]

        news_list = []
        news_json = []
        for news_info in iterate_news_list(start_date, end_date):
            publication_time = (news_info["news_publication_time"]
                                or news_info["news_preview_time"]
                                or news_info["news_creation_time"]
                                or news_info["news_prearranged_time"]
                                )
            publication_time = datetime.strptime(publication_time, "%Y-%m-%d %H:%M:%S")
            voice_id = news_info["news_easy_voice_uri"].split(".")[0]

            # Download Article content and voice file
            content:Content = self.download_content(news_info["news_id"],
                                                    save_dir.joinpath("contents"),
                                                    )
            voice:Voice = self.download_voice(voice_id,
                                              save_dir.joinpath("voices"),
                                              )

            news = News("NHK Easy Web",
                        news_info["news_id"],
                        news_info["title"],
                        content.url,
                        publication_time,
                        datetime.now(),
                        None,
                        voice,
                        content,
                        )
            news_list.append(news)
            news_json.append(news.to_json_dict())

        # Save news object 
        with open(save_dir.joinpath("news.json"), "w", encoding="utf-8") as file:
            json.dump(news_json, file, ensure_ascii=False, indent=4)
        self._news += news_list
        return news_list

if __name__ == "__main__":
    a = NHKEasyWebCrawler().download_recent_news()
    # a = NHKEasyWebCrawler().download_voice("k10014346261000_6mHAVGzMvPy7augGieIgIWnP8lt6zVMdzJEAxJdk")
    # print(a)
