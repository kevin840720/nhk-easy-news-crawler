# -*- encoding: utf-8 -*-
"""
@File:
    reader.py
@Time:
    2024/02/06 11:53:38
@Author:
    Kevin Wang
@Desc:
    資料讀取
"""

import json
import time
from typing import Dict

from config import ProjectConfigs
from objects import News
from utils import MyRequests

from bs4 import BeautifulSoup

class NewsLocalStorage:
    def __init__(self) -> None:
        self._data = None
        self._path = None
    
    def load(self,
             directory:str=ProjectConfigs.PROCESSED_DIR.joinpath("news"),
             ):
        
        self._data = ...
        self._path = directory
        return

    def add(self,):
        pass

        # if response.status_code != 200:
        #     print(f"""Request fail.
        #            Status Code: {response.status_code}
        #            URL: {self.last_url}
        #            PARAMS: {self.last_params}
        #            """)