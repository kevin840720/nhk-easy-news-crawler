# -*- encoding: utf-8 -*-
"""
@File    :  parser.py
@Time    :  2024/12/05 19:43:15
@Author  :  Kevin Wang
@Desc    :  None
"""

from typing import Optional
import json

from bs4 import BeautifulSoup

class NHKEasyNewsWebParser:
    def __init__(self,
                 soup:BeautifulSoup,
                 ) -> None:
        self.soup = soup

    @property
    def title(self) -> str:
        title_block = (self.soup.find("h1", {"class": "article-title"})
                       or self.soup.find("h1", {"class": "article-main__title"})  # 2024/04/01 之前
                       )
        for rt_tag in title_block.find_all("rt"):
            rt_tag.decompose()
        return title_block.text

    @property
    def date(self) -> str:
        date_block = (self.soup.find("p", {"class": "article-date"})
                      or self.soup.find("p", {"class": "article-main__date"})  # 2024/04/01 之前
                      )
        return date_block.text

    @property
    def body(self) -> str:
        body_block = (self.soup.find("div", {"class": "article-body"})
                      or self.soup.find("div", {"class": "article-main__body article-body"})  # 2024/04/01 之前
                      )
        for rt_tag in body_block.find_all("rt"):
            rt_tag.decompose()
        return body_block.text

class NHKNewsWebParser:
    def __init__(self,
                 soup:BeautifulSoup,
                 ) -> None:
        self.soup = soup

    def _get_article_meta(self) -> Optional[dict]:
        scripts = self.soup.find_all('script', type='application/ld+json')
        # 過濾只包含 "@type": "NewsArticle" 的 JSON
        for script in scripts:
            try:
                data = json.loads(script.string)  # 將 JSON 字串解析為 Python 字典
                if data.get("@type") == "NewsArticle":  # 檢查 @type 是否為 NewsArticle
                    return data
            except json.JSONDecodeError:
                continue

    @property
    def title(self):
        meta_data = self._get_article_meta()
        if meta_data:
            return meta_data["headline"]

        # 如果抓不到 meta data ，則直接從文章中爬取
        title_block = self.soup.find("h1", {"class": "content--title"})
        if title_block:
            return title_block.text
        return None

    @property
    def genre(self):
        meta_data = self._get_article_meta()
        if meta_data:
            return meta_data["genre"]
        return []

    @property
    def keywords(self):
        meta_data = self._get_article_meta()
        if meta_data:
            return meta_data["keywords"]
        return []

    @property
    def published_date(self):
        meta_data = self._get_article_meta()
        if meta_data:
            return meta_data["datePublished"]
        return None

    @property
    def modified_date(self):
        meta_data = self._get_article_meta()
        if meta_data:
            return meta_data["dateModified"]
        return None

    @property
    def date(self):
        date_block = self.soup.find("p", {"class": "content--date"})
        if date_block:
            return date_block.find("time").text
        return None

    @property
    def summary(self):
        block = self.soup.find("p", {"class": "content--summary"})
        if block:
            return block.text
        return None

    @property
    def body(self):
        block = self.soup.find("div", {"class": "content--detail-more"})
        if block:
            return block.text
        return None
