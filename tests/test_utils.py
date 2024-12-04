# -*- encoding: utf-8 -*-
"""
@File    :  test_utils.py
@Time    :  2024/12/04 20:48:15
@Author  :  Kevin Wang
@Desc    :  None
"""
import datetime

import pytest

from src.utils import NHKEasyNewsClient

class TestNHKEasyNewsClient:
    client = NHKEasyNewsClient()

    def test_get_news_summary(self):
        summary = self.client.get_news_summary()

        assert isinstance(summary, dict), "Expected data to be a dictionary"
        assert len(summary) > 0, "Expected data to have at least one entry"

        # 確定回傳 key 是日期結構
        first_key = list(summary.keys())[0]
        try:
            datetime.datetime.strptime(first_key, "%Y-%m-%d")
        except ValueError:
            assert False, f"Key '{first_key}' is not a valid date in 'YYYY-MM-DD' format"

    def test_get_content(self):
        # 拿取最新新聞的 id
        summary = self.client.get_news_summary()
        date, news = summary.popitem()
        news_id = news[0]['news_id']

        # 測試 get_content 方法
        response = self.client.get_content(news_id)
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        assert news_id in response.text, f"Expected news_id {news_id} in response text"
