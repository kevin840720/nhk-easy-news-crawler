# -*- encoding: utf-8 -*-
"""
@File:
    objects.py
@Time:
    2024/02/06 11:53:38
@Author:
    Kevin Wang
@Desc:
    自定義物件
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

@dataclass
class Media:
    status:str
    id:str
    url:str
    filepath:Path=None
    publication_time:Optional[datetime]=None
    download_time:Optional[datetime]=None

    def to_json_dict(self):
        data = {}
        data['id'] = self.id
        data = {**data, **asdict(self)}

        if data['publication_time'] is not None:
            data['publication_time'] = data['publication_time'].isoformat()
        if data['download_time'] is not None:
            data['download_time'] = data['download_time'].isoformat()
        if data['filepath'] is not None:
            data['filepath'] = self.filepath.__str__()
        return data

@dataclass
class HTMLContent:
    status:str
    id:str
    url:str
    filepath:Path
    title:Optional[str]=None
    article:Optional[str]=None
    publication_time:Optional[datetime]=None
    download_time:Optional[datetime]=None
    html:Optional[str]=None

    def to_json_dict(self):
        data = {}
        data['id'] = self.id
        data = {**data, **asdict(self)}

        if data['publication_time'] is not None:
            data['publication_time'] = data['publication_time'].isoformat()
        if data['download_time'] is not None:
            data['download_time'] = data['download_time'].isoformat()
        if data['filepath'] is not None:
            data['filepath'] = self.filepath.__str__()
        data.pop("html")  # 不要儲存原始 html

        return data

@dataclass
class News:
    source:str
    source_id:str
    title:str
    url:str
    publication_time:Optional[datetime]=None
    download_time:Optional[datetime]=None
    author:Optional[str]=None
    media:Optional[Media]=None
    html_content:Optional[HTMLContent]=None

    @property
    def id(self) -> int:
        # In binary, 0x7FFFFFFF becomes 01111111 11111111 11111111 11111111
        return hash((self.source, self.source_id)) & 0x7FFFFFFF
    
    def to_json_dict(self) -> dict:
        data = {}
        data['id'] = self.id
        data = {**data, **asdict(self)}

        if data['publication_time'] is not None:
            data['publication_time'] = data['publication_time'].isoformat()
        if data['download_time'] is not None:
            data['download_time'] = data['download_time'].isoformat()
        if data['media'] is not None:
            data['media'] = self.media.to_json_dict()
        if data['html_content'] is not None:
            data['html_content'] = self.html_content.to_json_dict()

        return data
