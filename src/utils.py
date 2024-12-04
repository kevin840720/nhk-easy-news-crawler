# -*- encoding: utf-8 -*-
"""
@File    :  utils.py
@Time    :  2024/02/06 12:00:08
@Author  :  Kevin Wang
@Desc    :  None
"""

from enum import Enum
from pathlib import Path
from time import (sleep,
                  time,
                  )
from typing import (Literal,
                    List,
                    Optional,
                    )
import json

from Crypto.Cipher import AES
import requests

# -*- encoding: utf-8 -*-
"""
@File    :  main.py
@Time    :  2024/05/02 15:51:37
@Author  :  Kevin Wang
@Desc    :  本程式主要用於下載和合併使用 HTTP Live Streaming (HLS) 協議的多媒體資料。HLS 將視頻內容 分割成數個較小的段落，每個段落都
            通過 HTTP 協議以 TS (運輸流格式) 文件形式傳輸，利用 M3U8 播放列表來管理這些 TS 文件的索引。本類別的目的是從指定的 M3U8 播放
            列表 URL 中抓取所有 TS 文件連結，下載這些文件，並最終合併成一個單一的多媒體文件。

            爬蟲流程：
            1. 解析 M3U8 播放列表以獲得 TS 文件的 URL。
            2. 下載所有 TS 文件。
            3. 將下載的 TS 文件合併成一個完整的視頻文件。
"""

from pathlib import Path
from typing import (List,
                    Union,
                    )
from urllib.parse import urljoin
import re


import m3u8

class MyRequests:
    def __init__(self) -> None:
        """
        A custom requests wrapper to handle HTTP requests with enhanced retry and session management.

        This class provides a flexible interface for making HTTP requests with built-in 
        retry mechanisms, session tracking, and customizable headers. It helps manage 
        connection issues and provides detailed tracking of request information.

        Attributes:
            _session (requests.Session): A persistent session for making HTTP requests.
            _headers (dict): Default headers used in requests.
            _html_parser (str): Default HTML parser used for parsing responses.
            _last_url (str): URL of the most recent request.
            _last_header (dict): Headers used in the most recent request.
            _last_params (dict): Parameters used in the most recent request.
            _last_response (requests.Response): Response of the most recent request.
        """
        self._session = requests.Session()
        self._headers = {'Content-Type': 'application/x-www-form-urlencoded',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'User-Agent': 'PostmanRuntime/7.28.4'}
        self._html_parser = "html.parser"

        # last requests
        self._last_url = None
        self._last_header = None
        self._last_params = None
        self._last_response = None

    @property
    def session_id(self) -> str:
        """
        Retrieve the session cookie ID.

        Returns:
            str: The value of the session cookie.
        """
        return self._session.cookies.get('session_cookie_name')

    @property
    def headers(self) -> dict:
        """
        Get the current headers used in requests.

        Returns:
            dict: The current headers dictionary.
        """
        return self._headers

    @headers.setter
    def headers(self, obj):
        """
        Set new headers for future requests.

        Args:
            obj (dict): A dictionary of headers to use in requests.

        Returns:
            dict: The newly set headers.
        """
        self._headers = obj
        return obj

    def request(self,
                method,
                url,
                lapse=0.1,
                max_retry=100,
                timeout=90,
                **kwargs
                ) -> requests.Response:
        """
        Send an HTTP request with built-in retry and error handling.

        Attempts to send a request, handling timeouts and connection errors 
        by retrying up to a maximum number of attempts.

        Args:
            method (str): HTTP method (GET, POST, etc.).
            url (str): The URL to send the request to.
            lapse (float, optional): Time to wait between retries. Defaults to 0.1 seconds.
            max_retry (int, optional): Maximum number of retry attempts. Defaults to 100.
            timeout (int, optional): Request timeout in seconds. Defaults to 90 seconds.
            **kwargs: Additional arguments to pass to requests.Session.request.

        Returns:
            requests.Response: The response from the server.

        Raises:
            TimeoutError: If no response is received after maximum retries.
        """
        retry = 0
        while True:
            try:
                self._last_url = url
                self._last_params = kwargs.get("params")
                response = self._session.request(method,
                                                 url,
                                                 headers=self.headers,
                                                 timeout=timeout,
                                                 **kwargs
                                                 )
                self._last_response = response
                print(response.url)
                sleep(lapse)
                break
            except requests.exceptions.ReadTimeout:
                print('Read timed out. retry...')
                retry = retry + 1
                sleep(lapse)
            except requests.exceptions.ConnectionError:
                print('Read timed out. retry...')
                retry = retry + 1
                sleep(lapse)
            # except Exception as err:
            #     print(f'Unknown error {err}')
            #     retry = retry + 1
            #     sleep(lapse)
            if retry >= max_retry:
                raise TimeoutError('No response, check your internet.')
        return response

class HLSMediaDownloader:
    def __init__(self) -> None:
        """本程式主要用於下載和合併使用 HTTP Live Streaming (HLS) 協議的多媒體資料。
        
        Note:
            HLS 將視頻內容 分割成數個較小的段落，每個段落都通過 HTTP 協議以 TS (運輸流格式) 文件形式傳輸，利用 M3U8 播放列表來管理這些
            TS 文件的索引。本類別的目的是從指定的 M3U8 播放列表 URL 中抓取所有 TS 文件連結，下載這些文件，並最終合併成一個單一的多媒體文件。
        """
        self._requestor = MyRequests()

    def fetch_playlist(self,
                       m3u8_url:str,
                       ) -> List[m3u8.M3U8]:
        """Fetch and flatten all M3U8 playlists, including nested playlists, from the given M3U8 URL.

        This function recursively resolves variant M3U8 playlists to extract and return a list
        of all non-variant playlists that directly reference TS files.

        Args:
            m3u8_url (str): URL of the M3U8 playlist, for example https://example.com/master.m3u8

        Returns:
            List[m3u8.M3U8]: Playlists containing only TS segments

        Notes:
            - If the provided M3U8 is a variant playlist, it will recursively resolve all sub-playlists
              until only non-variant playlists remain.
        """

        def get_m3u8s(obj:m3u8.M3U8):
            playlists = []
            if obj.is_variant:
                for playlist in obj.playlists:
                    sub_playlist = m3u8.load(playlist.base_uri + playlist.uri)
                    playlists += get_m3u8s(sub_playlist)
                return playlists
            return [obj]

        playlist = m3u8.load(m3u8_url)
        playlists = get_m3u8s(playlist)
        print(playlists[0].__dict__)
        return playlists

    def download_m3u8(self,
                      playlist:m3u8.M3U8,
                      ) -> bytes:
        """
        Download all TS segments from an M3U8 playlist and return their combined binary content.

        Args:
            playlist (m3u8.M3U8): The parsed M3U8 playlist object.

        Returns:
            bytes: The combined binary content of all TS segments.
        """
        # Retrieve AES key if encryption is used
        aes_key = None
        if len(playlist.keys) > 0:
            key:m3u8.Key = playlist.keys[0]
            key_url = urljoin(key.base_uri, key.uri)
            key_response = self._requestor.request("GET", key_url)
            aes_key = key_response.content
        

        combined_segments = b""
        for segment in playlist.segments:
            # Download and process each TS segment
            ts_url = urljoin(segment.base_uri, segment.uri)
            response = self._requestor.request("GET", ts_url)
            segment_content = response.content

            # Decrypt the segment if an AES key is provided
            if aes_key:
                segment_content = self.decrypt_segment(segment_content, aes_key)

            combined_segments += segment_content
        return combined_segments

    def decrypt_segment(self, segment, key):
        """Decrypt a single TS segment using AES CBC mode.

        Args:
            segment (bytes): Encrypted segment content
            key (bytes): Decryption key

        Returns:
            bytes: Decrypted segment content
        """
        cipher = AES.new(key, AES.MODE_CBC, iv=b'\x00'*16)  # 初始化向量通常為零
        return cipher.decrypt(segment)

    def save(self,
             m3u8_url:str,
             filename:Union[str,Path],
             ) -> None:
        """Download and save media from an M3U8 playlist.

        Fetches playlist, downloads segments, and saves to file.

        Args:
            m3u8_url (str): URL of the M3U8 playlist
            filename (Union[str, Path]): Output file path

        Raises:
            ValueError: If no playlists are found
        """
        playlists = self.fetch_playlist(m3u8_url)
        if len(playlists) == 0:
            raise ValueError("No audio download")

        combined_segments = b""
        for playlist in playlists:
            combined_segments += self.download_m3u8(playlist)

        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        with open(filename, "wb") as file:
            file.write(combined_segments)
        print(f"All TS files have been merged into {filename}")

class NHKEasyNewsClient:
    def __init__(self):
        """
        A specialized web crawler for NHK Easy News content retrieval.

        This class provides methods to fetch various types of content from the NHK Easy News 
        website, including news lists, article content, and voice recordings.

        Attributes:
            crawler (MyRequests): A custom requests handler for making web requests.
            _payload (dict): Optional payload for requests (currently unused).
        """
        self.crawler = MyRequests()
        self.crawler.headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0",
                                "Accept": "application/json, text/javascript, */*; q=0.01",
                                "Referer": "https://www3.nhk.or.jp/news/easy/",
                                }
        self._payload = {}

    @property
    def last_url(self) -> str:
        """
        Get the URL of the most recent request.

        Returns:
            str: The last requested URL.
        """
        return self.crawler._last_url

    @property
    def headers(self) -> str:
        """
        Get the current request headers.

        Returns:
            str: The current headers being used for requests.
        """
        return self.crawler.headers

    @property
    def last_params(self) -> dict:
        """
        Get the parameters of the most recent request.

        Returns:
            dict: The parameters used in the last request.
        """
        return self.crawler._last_params

    @property
    def last_response(self) -> requests.Response:
        """
        Get the most recent response.

        Returns:
            requests.Response: The response from the most recent request.
        """
        return self.crawler._last_response

    def get_news_summary(self) -> dict:
        """
        Retrieve a summary of news articles grouped by date from the past year.

        Sends a GET request to fetch the news list JSON from NHK Easy News.

        Returns:
            requests.Response: A response containing the news list in JSON format.
        """
        url = "https://www3.nhk.or.jp/news/easy/news-list.json"
        params = {"_": int(time()*1000),  # Unix time up to milliseconds (這像參數貌似不影響回傳結果)
                  }
        response = self.crawler.request(method="GET",
                                        url=url,
                                        params=params,
                                        )  # response 回傳長度為 1 的 List
        return json.loads(response.text)[0]

    def get_content(self,
                    id:str,
                    ) -> requests.Response:
        """
        Retrieve a news article's content using its ID.

        Args:
            id (str): Unique identifier for the news article.

        Returns:
            requests.Response: A response containing the HTML content of the article.
        """
        url = f"https://www3.nhk.or.jp/news/easy/{id}/{id}.html"
        response = self.crawler.request(method="GET",
                                        url=url,
                                        )
        return response

    def get_voice_m3u8_m4a_type(self,
                                uri:str,
                                ) -> requests.Response:
        """
        Retrieve the M4A voice recording for a news article.

        Args:
            uri (str): Unique identifier for the voice recording.

        Returns:
            requests.Response: A response containing the M4A voice recording's M3U8 playlist.
        """
        url = f"https://vod-stream.nhk.jp/news/easy_audio/{uri}/index.m3u8"
        response = self.crawler.request(method="GET",
                                        url=url,
                                        )
        return response

    def get_voice_m3u8_mp4_type(self,
                                uri:str,
                                ) -> requests.Response:
        """
        Retrieve the MP4 voice recording for a news article.

        Args:
            uri (str): Unique identifier for the voice recording.

        Returns:
            requests.Response: A response containing the MP4 voice recording's M3U8 playlist.
        """
        url = f"https://vod-stream.nhk.jp/news/easy/{uri}/index.m3u8"
        response = self.crawler.request(method="GET",
                                        url=url,
                                        )
        return response

    def get_voice_m3u8(self,
                       uri:str,
                       fmt:Literal["m4a", "mp4"]=None,
                       ) -> requests.Response:
        """
        Retrieve a voice recording, attempting both M4A and MP4 formats.

        Args:
            uri (str): Unique identifier for the voice recording.
            fmt (str, optional): Specific audio format to retrieve. 
                                 Can be 'm4a', 'mp4', or None (tries both).

        Returns:
            requests.Response: A response containing the voice recording's M3U8 playlist.

        Raises:
            ValueError: If an invalid audio format is specified.
        """
        if fmt not in [None, "m4a", "mp4"]:
            raise ValueError("Unknown audio type")
        formats = ["m4a", "mp4"] if fmt is None else [fmt]

        for format in formats:
            if format == "mp4":
                response = self.get_voice_m3u8_mp4_type(uri)
            elif format == "m4a":
                response = self.get_voice_m3u8_m4a_type(uri)

            if response.status_code == 200:
                return response
        return response

class NHKNewsType(Enum):
    social = 1
    culture = 2
    science = 3
    political = 4
    economic = 5
    international = 6
    sport = 7

class NHKNewsClient:
    def __init__(self):
        self.crawler = MyRequests()
        self.crawler.headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0",
                                "Accept": "application/json, text/javascript, */*; q=0.01",
                                "Referer": "https://www3.nhk.or.jp/news/easy/",
                                }
        self._payload = {}

    @property
    def last_url(self) -> str:
        """
        Get the URL of the most recent request.

        Returns:
            str: The last requested URL.
        """
        return self.crawler._last_url

    @property
    def headers(self) -> str:
        """
        Get the current request headers.

        Returns:
            str: The current headers being used for requests.
        """
        return self.crawler.headers

    @property
    def last_params(self) -> dict:
        """
        Get the parameters of the most recent request.

        Returns:
            dict: The parameters used in the last request.
        """
        return self.crawler._last_params

    @property
    def last_response(self) -> requests.Response:
        """
        Get the most recent response.

        Returns:
            requests.Response: The response from the most recent request.
        """
        return self.crawler._last_response

    def get_news_summary(self,
                      news_type:NHKNewsType,
                      sheet:int=1,
                      ) -> List[requests.Response]:
        """
        Retrieve the list of news articles from the past year.

        Sends a GET request to fetch the news list JSON from NHK Easy News.

        Returns:
            requests.Response: A response containing the news list in JSON format.
        """
        url = f"https://www3.nhk.or.jp/news/json16/cat{news_type.value:02d}_{sheet:03d}.json"

        params = {"_": int(time()),  # Unix time (這像參數貌似不影響回傳結果)
                    }
        response = self.crawler.request(method="GET",
                                        url=url,
                                        params=params,
                                        )
        return response

    def get_content(self,
                    date:str,
                    id:str,
                    ) -> requests.Response:
        """
        Retrieve a news article's content using its date and ID.

        Args:
            date (str): _description_
            id (str): Unique identifier for the news article.

        Returns:
            requests.Response: A response containing the HTML content of the article.
        """
        url = f"https://www3.nhk.or.jp/news/html/{date}/{id}.html"
        response = self.crawler.request(method="GET",
                                        url=url,
                                        )
        return response

    def get_video_mp4(self,
                      uri:str,
                      ) -> requests.Response:
        """
        Retrieve the MP4 voice recording for a news article.

        Args:
            uri (str): Unique identifier for the voice recording.

        Returns:
            requests.Response: A response containing the MP4 voice recording's M3U8 playlist.
        """
        url = f"https://vod-stream.nhk.jp/news/{uri}/index.m3u8"
        response = self.crawler.request(method="GET",
                                        url=url,
                                        )
        return response
