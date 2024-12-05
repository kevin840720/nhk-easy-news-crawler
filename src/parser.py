# -*- encoding: utf-8 -*-
"""
@File    :  parser.py
@Time    :  2024/12/05 19:43:15
@Author  :  Kevin Wang
@Desc    :  None
"""

from bs4 import BeautifulSoup

class NHKEasyNewsWebParser:
    def __init__(self,
                 soup:BeautifulSoup,
                 ) -> None:
        self.soup = soup

    def article_html(self):
        return self.soup.find("article", {"class": "easy-article"})

    @property
    def title(self):
        article_soup = self.article_html()
        title_block = article_soup.find("h1", {"class": "article-title"})
        for rt_tag in title_block.find_all("rt"):
            rt_tag.decompose()
        return title_block.text

    @property
    def date(self):
        article_soup = self.article_html()
        date_block = article_soup.find("p", {"class": "article-date"})
        return date_block.text

    @property
    def body(self):
        article_soup = self.article_html()
        body_block = article_soup.find("div", {"class": "article-body"})
        for rt_tag in body_block.find_all("rt"):
            rt_tag.decompose()
        return body_block.text
