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
from objects import (HTMLContent,
                     News,
                     Media,
                     )
from parser import (NHKEasyNewsWebParser,
                    NHKNewsWebParser,
                    )
from utils import (HLSMediaDownloader,
                   NHKEasyNewsClient,
                   NHKNewsClient,
                   NHKNewsType,
                   )

class NHKEasyWebCrawler:
    """A web crawler for NHK Easy News, designed to download news content and associated audio.

    This class provides methods to retrieve recent news articles from NHK Easy Web, 
    downloading both the articles and voice recordings for each news item within 
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
                       ) -> Media:
        """Download an audio voice recording for a specific news item.

        Args:
            voice_id (str): Unique identifier for the voice recording.
            voice_dir (Path, optional): Directory to save the voice file. 
                Defaults to a predefined path in project configurations.

        Returns:
            Media: An object representing the downloaded voice recording, 
                   containing metadata and file path.
        """
        response = self.crawler.get_voice_m3u8(voice_id)
        path = voice_dir.joinpath(f'{voice_id}.mp3')

        voice_dir.mkdir(exist_ok=True, parents=True)
        HLSMediaDownloader().save(response.url, path)
        return Media(status=response.status_code,
                     id=voice_id,
                     url=response.url,
                     filepath=path,
                     publication_time=None,
                     download_time=datetime.now(),
                     )

    def download_html(self,
                      content_id:str,
                      content_dir=ProjectConfigs.RAW_DIR.joinpath("nhk_easy_web/contents"),
                      ) -> HTMLContent:
        """Download the HTML content for a specific news article.

        Args:
            content_id (str): Unique identifier for the news article.
            content_dir (Path, optional): Directory to save the HTML content. 
                Defaults to a predefined path in project configurations.

        Returns:
            HTMLContent: An object representing the downloaded content, 
                         containing metadata and file path.
        """
        response = self.crawler.get_content(content_id)
        path = content_dir.joinpath(f'{content_id}.html')
        soup = BeautifulSoup(response.content, 'html.parser')
        parser = NHKEasyNewsWebParser(soup)

        content_dir.mkdir(exist_ok=True, parents=True)
        if response.status_code == 200:
            with open(path, 'wb') as file:
                file.write(response.content)
        try:
            publication_time = datetime.strptime(parser.date, "%Y年%m月%d日 %H時%M分")
        except ValueError:
            publication_time = None
        return HTMLContent(status=response.status_code,
                           id=content_id,
                           url=response.url,
                           filepath=path,
                           title=parser.title,
                           article=parser.body,
                           publication_time=publication_time,
                           download_time=datetime.now(),
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
        start_date = start_date.date() if start_date else (datetime.now() - timedelta(days=365)).date()
        end_date = end_date.date() if end_date else datetime.now().date()
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
            html_content:HTMLContent = self.download_html(news_info["news_id"],
                                                          save_dir.joinpath("contents"),
                                                          )
            voice:Media = self.download_voice(voice_id,
                                              save_dir.joinpath("voices"),
                                              )

            news = News("NHK Easy Web",
                        news_info["news_id"],
                        news_info["title"],
                        html_content.url,
                        publication_time,
                        datetime.now(),
                        None,
                        voice,
                        html_content,
                        )
            news_list.append(news)
            news_json.append(news.to_json_dict())

        # Save news object 
        with open(save_dir.joinpath("news.json"), "w", encoding="utf-8") as file:
            json.dump(news_json, file, ensure_ascii=False, indent=4)
        self._news += news_list
        return news_list

class NHKWebCrawler:
    """A web crawler for NHK News, designed to download news content and associated video.

    This class provides methods to retrieve recent news articles from NHK News, 
    downloading both the articles and video recordings for each news item within 
    a specified date range.

    Example:
        crawler = NHKEasyWebCrawler()
        # Get news from the last 30 days
        recent_news = crawler.download_recent_news(
            start_date=datetime.now() - timedelta(days=30)
        )
    """
    def __init__(self):
        self.crawler = NHKNewsClient()
        self._news = []

    def download_video(self,
                       video_id:str,
                       video_dir=ProjectConfigs.RAW_DIR.joinpath("nhk_news/video"),
                       ) -> Media:
        """Download an audio voice recording for a specific news item.

        Args:
            voice_id (str): Unique identifier for the video recording.
            voice_dir (Path, optional): Directory to save the video file. 
                Defaults to a predefined path in project configurations.

        Returns:
            Media: An object representing the downloaded video recording, 
                   containing metadata and file path.
        """
        response = self.crawler.get_video_m3u8(video_id)
        path = video_dir.joinpath(f'{video_id}.mp4')

        video_dir.mkdir(exist_ok=True, parents=True)
        HLSMediaDownloader().save(response.url, path)
        return Media(status=response.status_code,
                     id=video_id,
                     url=response.url,
                     filepath=path,
                     publication_time=None,
                     download_time=datetime.now(),
                     )

    def download_html(self,
                      date:str,
                      content_id:str,
                      content_dir=ProjectConfigs.RAW_DIR.joinpath("nhk_news/contents"),
                      ) -> HTMLContent:
        """Download the HTML content for a specific news article.

        Args:
            content_id (str): Unique identifier for the news article.
            content_dir (Path, optional): Directory to save the HTML content. 
                Defaults to a predefined path in project configurations.

        Returns:
            HTMLContent: An object representing the downloaded content, 
                         containing metadata and file path.
        """
        response = self.crawler.get_content(date, content_id)
        path = content_dir.joinpath(f'{content_id}.html')
        soup = BeautifulSoup(response.content, 'html.parser')
        parser = NHKNewsWebParser(soup)

        content_dir.mkdir(exist_ok=True, parents=True)
        if response.status_code == 200:
            with open(path, 'wb') as file:
                file.write(response.content)
        
        # Get publication_time
        pairs = [(parser.published_date, "%Y-%m-%dT%H:%M:%S%z"),
                 (parser.modified_date, "%Y-%m-%dT%H:%M:%S%z"),
                 (parser.date, "%Y年%m月%d日 %H時%M分"),
                 ]
        publication_time = None
        for val, fmt in pairs:
            if not val:
                continue
            try:
                publication_time = datetime.strptime(val, fmt)
            except ValueError:
                continue

        return HTMLContent(status=response.status_code,
                           id=content_id,
                           url=response.url,
                           filepath=path,
                           title=parser.title,
                           article=parser.body,
                           publication_time=publication_time,
                           download_time=datetime.now(),
                           html=response.text,
                           )

    def download_recent_news(self,
                             start_date:datetime=None,
                             end_date:datetime=None,
                             save_dir=ProjectConfigs.RAW_DIR.joinpath("nhk_news"),
                             ):
        """Retrieve recent news articles within a specified date range.

        This method fetches news articles from NHK News, downloading both content and video (if exists) for each article.
        By default, it retrieves news from the past 10 days.

        Args:
            start_date (datetime, optional): The earliest date to retrieve news from. 
                Defaults to 10 days ago from the current date.
            end_date (datetime, optional): The latest date to retrieve news to. 
                Defaults to the current date.
            save_dir (_type_, optional): _description_. Defaults to ProjectConfigs.RAW_DIR.joinpath("nhk_news").

        Returns:
            List[News]: A list of News objects containing article details, 
                        content, and voice recordings.

        Raises:
            ValueError: If the start date is more than one year in the past.
        """
        start_date = start_date.date() if start_date else (datetime.now() - timedelta(days=10)).date()
        end_date = end_date.date() if end_date else datetime.now().date()

        def iterate_news_list(start_date, end_date) -> dict:
            for news_type in NHKNewsType:
                summary = self.crawler.get_news_summary(news_type)
                news_list = summary["channel"]["item"]
                for news in news_list:
                    date = datetime.strptime(news["pubDate"], "%a, %d %b %Y %H:%M:%S %z").date()
                    if date < start_date or date > end_date:
                        continue
                    yield news

        news_list = []
        news_json = []
        for news_info in iterate_news_list(start_date, end_date):
            publication_time = datetime.strptime(news_info["pubDate"], "%a, %d %b %Y %H:%M:%S %z")

            # Download article
            _, link_date, identifier = news_info["link"].replace(".html", "").split("/")
            html_content:HTMLContent = self.download_html(date=link_date,
                                                          content_id=identifier,
                                                          content_dir=save_dir.joinpath("contents"),
                                                          )

            # Download video (if exists)
            video = None
            if news_info["videoPath"]:
                video_id = news_info["videoPath"].replace(".mp4", "")
                video:Media = self.download_video(video_id,
                                                  save_dir.joinpath("videos"),
                                                  )

            news = News("NHK News",
                        f"{link_date}-{identifier}",
                        news_info["title"],
                        html_content.url,
                        publication_time,
                        datetime.now(),
                        None,
                        video,
                        html_content,
                        )
            if not news.html_content.title or not news.html_content.article:
                print(f"Lack of title or article: {news.url}, skipped")
                continue
            news_list.append(news)
            news_json.append(news.to_json_dict())

        # Save news object 
        with open(save_dir.joinpath("news.json"), "w", encoding="utf-8") as file:
            json.dump(news_json, file, ensure_ascii=False, indent=4)
        self._news += news_list
        return news_list

if __name__ == "__main__":
    # NHKEasyWebCrawler().download_recent_news()
    NHKWebCrawler().download_recent_news()
    # from utils import NHKNewsType, NHKNewsClient
    # a = NHKNewsClient().get_news_summary(NHKNewsType.culture)
    # b = NHKWebCrawler().download_video("k10014660111_202412061226_202412061228")
    # a = NHKEasyWebCrawler().download_voice("k10014346261000_6mHAVGzMvPy7augGieIgIWnP8lt6zVMdzJEAxJdk")
