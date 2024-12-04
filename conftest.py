# -*- encoding: utf-8 -*-
"""
@File:
    conftest.py
@Time:
    2023/08/24 13:34:58
@Author:
    Kevin Wang
@Desc:
    None
@Ref:
    https://stackoverflow.com/questions/42996270/change-pytest-rootdir
"""

from pathlib import Path
import sys

scripts_path = Path(__file__).parent.joinpath('src')
sys.path.append(scripts_path.__str__())
