# -*- encoding: utf-8 -*-
"""
@File    :  utils.py
@Time    :  2024/02/06 12:00:08
@Author  :  Kevin Wang
@Desc    :  None
"""

from time import (sleep,
                  time,
                  )
from typing import Literal

import requests

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

    def get_news_list(self) -> requests.Response:
        """
        Retrieve the list of news articles from the past year.

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
                                        )
        return response

    def get_content(self,
                    date_code:str,  # YYYYMMDD
                    id:str,
                    ) -> requests.Response:
        """
        Retrieve a specific news article's content.

        Args:
            date_code (str): Date in YYYYMMDD format.
            id (str): Unique identifier for the news article.

        Returns:
            requests.Response: A response containing the HTML content of the article.
        """
        url = f"https://www3.nhk.or.jp/news/easy/{date_code}/{id}.html"
        response = self.crawler.request(method="GET",
                                        url=url,
                                        )
        return response

    def get_easy_content(self,
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

    def get_voice_m4a(self,
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

    def get_voice_mp4(self,
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

    def get_voice(self,
                  uri:str,
                  fmt:Literal["m4a", "mp4"],
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
                response = self.get_voice_mp4(uri)
            elif format == "m4a":
                response = self.get_voice_m4a(uri)

            if response.status_code == 200:
                return response
        return response

