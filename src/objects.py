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
from typing import Any
import json

@dataclass
class Voice:
    status:str
    id:str=None
    url:str=None
    publication_time:datetime=None
    download_time:datetime=None
    location:Path=None

    def to_json_dict(self):
        data = {}
        data['id'] = self.id
        data = {**data, **asdict(self)}

        if data['publication_time'] is not None:
            data['publication_time'] = data['publication_time'].isoformat()
        if data['download_time'] is not None:
            data['download_time'] = data['download_time'].isoformat()
        if data['location'] is not None:
            data['location'] = self.location.__str__()

        return data

@dataclass
class Content:
    status:str
    id:str=None
    url:str=None
    title:str=None
    article:str=None
    publication_time:datetime=None
    download_time:datetime=None
    location:Path=None
    html:str=None

    def to_json_dict(self):
        data = {}
        data['id'] = self.id
        data = {**data, **asdict(self)}

        if data['publication_time'] is not None:
            data['publication_time'] = data['publication_time'].isoformat()
        if data['download_time'] is not None:
            data['download_time'] = data['download_time'].isoformat()
        if data['location'] is not None:
            data['location'] = self.location.__str__()
        data.pop("html")  # 不要儲存原始 html

        return data

@dataclass
class News:
    source:str
    source_id:str
    title:str
    url:str
    publication_time:datetime=None
    download_time:datetime=None
    author:str=None
    voice:Voice=None
    content:Content=None

    @property
    def id(self):
        hash((self.source, self.source_id))
    
    def to_json_dict(self):
        data = {}
        data['id'] = self.id
        data = {**data, **asdict(self)}

        if data['publication_time'] is not None:
            data['publication_time'] = data['publication_time'].isoformat()
        if data['download_time'] is not None:
            data['download_time'] = data['download_time'].isoformat()
        if data['voice'] is not None:
            data['voice'] = self.voice.to_json_dict()
        if data['content'] is not None:
            data['content'] = self.content.to_json_dict()

        return data
