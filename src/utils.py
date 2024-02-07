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

import requests

class MyRequests:
    def __init__(self) -> None:
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
    def session_id(self):
        return self._session.cookies.get('session_cookie_name')

    @property
    def headers(self):
        return self._headers

    @headers.setter
    def headers(self, obj):
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

class NHKEasyWebRequests:
    def __init__(self):
        self.crawler = MyRequests()
        self.crawler.headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0",
                                "Accept": "application/json, text/javascript, */*; q=0.01",
                                "Referer": "https://www3.nhk.or.jp/news/easy/",
                                }
        self._payload = {}

    @property
    def last_url(self) -> str:
        return self.crawler._last_url

    @property
    def headers(self) -> str:
        return self.crawler.headers

    @property
    def last_params(self) -> dict:
        return self.crawler._last_params

    @property
    def last_response(self) -> requests.Response:
        return self.crawler._last_response

    def get_news_list(self) -> requests.Response:
        """獲取一年內的新聞列表
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
        url = f"https://www3.nhk.or.jp/news/easy/{date_code}/{id}.html"
        response = self.crawler.request(method="GET",
                                        url=url,
                                        )
        return response

    def get_easy_content(self,
                         id:str,
                         ) -> requests.Response:
        url = f"https://www3.nhk.or.jp/news/easy/{id}/{id}.html"
        response = self.crawler.request(method="GET",
                                        url=url,
                                        )
        return response

    def get_voice_m4a(self,
                      uri:str,
                      ) -> requests.Response:
        url = f"https://vod-stream.nhk.jp/news/easy_audio/{uri}/index.m3u8"
        response = self.crawler.request(method="GET",
                                        url=url,
                                        )
        return response

    def get_voice_mp4(self,
                      uri:str,
                      ) -> requests.Response:
        url = f"https://vod-stream.nhk.jp/news/easy/{uri}/index.m3u8"
        response = self.crawler.request(method="GET",
                                        url=url,
                                        )
        return response

    def get_voice(self,
                  uri:str,
                  fmt:str=None,
                  ) -> requests.Response:
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