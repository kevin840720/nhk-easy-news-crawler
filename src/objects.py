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
from typing import Any
import json

@dataclass
class News:
    source:str
    source_id:str
    title:str
    url:str
    date:datetime=None
    author:str=None
    voice:Any=None
    voice_url:str=None
    text:str=None
    _raw:str=None

    @property
    def id(self):
        hash((self.source, self.source_id))
    
    def to_json(self):
        data = {}
        data['id'] = self.id
        data = {**data, **asdict(self)}

        if data['date'] is not None:
            data['date'] = data['date'].isoformat()

        return json.dumps(data, ensure_ascii=False)
