# -*- encoding: utf-8 -*-
"""
@File    :  test_parser.py
@Time    :  2024/12/05 21:58:15
@Author  :  Kevin Wang
@Desc    :  None
"""
import datetime
import re

import pytest
from bs4 import BeautifulSoup

from src.parser import NHKEasyNewsWebParser

class TestNHKEasyWebCrawler:
    html_filepath = "tests/data/ne2024120411451.html"
    with open(html_filepath, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file.read(), "html.parser")
    parser = NHKEasyNewsWebParser(soup)

    def test_title(self):
        text = re.sub(r"\s", "", self.parser.title)
        assert text == "中村さんが亡くなってから5年アフガニスタンに新しい水路"

    def test_date(self):
        text = re.sub(r"\s", "", self.parser.date)
        assert text == "2024年12月4日19時23分"

    def test_body(self):
        text = re.sub(r"\s", "", self.parser.body)
        assert text == "アフガニスタンで、水がない乾いた場所を畑に変えた日本人がいます。医師の中村哲さんです。中村さんは、5年前の12月4日、アフガニスタンで誰かに銃で撃たれて亡くなりました。中村さんは、畑で食べ物を育てることができるように、水が通る水路を作っていました。中村さんと同じ気持ちの人たちが、いまも水路を作り続けています。3日、新しい水路に水を通す式がありました。作った人は「水が通るのを見ると、とてもうれしいです。これからも続けます」と話しました。新しい水路ができて、近くに住んでいる人たちの生活がよくなりそうです。"
