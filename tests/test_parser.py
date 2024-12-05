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

from src.parser import (NHKEasyNewsWebParser,
                        NHKNewsWebParser,
                        )

class TestNHKEasyWebCrawlerBefore20240401:
    """NHK Easy News 在 20240401 對網站進行改版
    """
    html_filepath = "tests/data/k10014405081000.html"
    with open(html_filepath, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file.read(), "html.parser")
    parser = NHKEasyNewsWebParser(soup)

    def test_title(self):
        text = re.sub(r"\s", "", self.parser.title)
        assert text == "障害がある人をどうやって手伝うか東京の会社が勉強会"

    def test_date(self):
        text = re.sub(r"\s", "", self.parser.date)
        assert text == "[04月01日12時00分]"

    def test_body(self):
        text = re.sub(r"\s", "", self.parser.body)
        assert text == ("4月から法律が変わって、障害がある人が困っているときは、役所だけではなくて、会社もできるだけ手伝いをしなければ"
                        "なりません。東京の会社は、障害がある人とどうやってコミュニケーションをしたらいいか勉強する会を開きました。"
                        "40人ぐらいの社員が参加しました。会では、声が出ない人が来たときに、どうしたらいいか考えました。パソコンに字を"
                        "入れたら読んでくれるソフトを使って会話を体験しました。そのあと、耳が聞こえない人が来たら、何ができるか考えました。"
                        "手話ができる社員をすぐに呼んだほうがいいという意見などが出ました。この会を計画した社員は「法律ができても、"
                        "社会はすぐに変わらないと思います。しかし、少しずつ変わっていくかもしれません」と話しました。"
                        )

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
        assert text == ("アフガニスタンで、水がない乾いた場所を畑に変えた日本人がいます。医師の中村哲さんです。中村さんは、5年前の12月4日、"
                        "アフガニスタンで誰かに銃で撃たれて亡くなりました。中村さんは、畑で食べ物を育てることができるように、水が通る水路を"
                        "作っていました。中村さんと同じ気持ちの人たちが、いまも水路を作り続けています。3日、新しい水路に水を通す式がありま"
                        "した。作った人は「水が通るのを見ると、とてもうれしいです。これからも続けます」と話しました。新しい水路ができて、"
                        "近くに住んでいる人たちの生活がよくなりそうです。")

class TestNHKNewsWebParser:
    html_filepath = "tests/data/k10014659321000.html"
    with open(html_filepath, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file.read(), "html.parser")
    parser = NHKNewsWebParser(soup)

    def test_title(self):
        text = re.sub(r"\s", "", self.parser.title)
        assert text == "【ライブ中】JAXA「イプシロンS」先月の爆発事故調査状況説明"

    def test_genre(self):
        assert self.parser.genre == ["社会","科学・文化"]

    def test_keywords(self):
        assert self.parser.keywords == ["宇宙","鹿児島県","ニュース深掘り"]

    def test_published_date(self):
        text = re.sub(r"\s", "", self.parser.published_date)
        assert text == "2024-12-05T16:00:51+09:00"

    def test_modified_date(self):
        text = re.sub(r"\s", "", self.parser.modified_date)
        assert text == "2024-12-05T16:21:28+09:00"

    def test_date(self):
        text = re.sub(r"\s", "", self.parser.date)
        assert text == "2024年12月5日16時00分"

    def test_summary(self):
        text = re.sub(r"\s", "", self.parser.summary)
        assert text == ("先月26日、鹿児島県の種子島宇宙センターで行われた、開発中の日本の新たな主力ロケット「イプシロンS」の燃焼試験で発生"
                        "した爆発事故について、JAXA＝宇宙航空研究開発機構は、原因調査の進捗（しんちょく）状況を説明します。午後4時から"
                        "始まった記者会見をライブ配信でお伝えしています。")

    def test_body(self):
        text = re.sub(r"\s", "", self.parser.body)
        assert text == ("《事故の経緯》先月26日の午前8時半ごろ、種子島宇宙センターで行われた固体燃料式の小型ロケット「イプシロンS」の2段目"
                        "の燃焼試験で、燃焼中に異常が発生しました。JAXAなどによりますと、試験はおよそ120秒間行われる計画でしたが、"
                        "燃焼開始後20秒ほどから燃料を燃やす容器内の圧力が予測より徐々に高くなり、49秒後に爆発したということです。"
                        "この爆発で試験場で火災が発生し消火活動が行われましたが、けが人はいませんでした。"
                        "試験場の周辺には爆発したロケットの部品などが飛び散り、JAXAは部品を回収するとともに、試験で取得した200項目の"
                        "データを評価するなどして、爆発の詳しい原因を究明するとしています。「イプシロンS」は、JAXAなどが開発中の日本の"
                        "主力ロケットの1つで、去年7月に秋田県の試験場で行われた同じ2段目の燃焼試験では、"
                        "試験開始からおよそ57秒後に爆発事故が発生しました。JAXAは前回の爆発の原因を特定し、対策をとった上で、"
                        "今回の再試験に臨んだとしていますが、今回の爆発と前回の爆発事故に共通するデータの傾向も"
                        "見られるとして詳しく調べることにしています。「イプシロンS」は世界で需要が高まる衛星打ち上げビジネスへの参入を"
                        "目指して開発が進められていますが、今後の打ち上げ計画への影響は避けられない見通しです。"
                        "【詳しくはこちら】小型ロケット「イプシロンS」燃焼試験で爆発去年に続き2回目")
