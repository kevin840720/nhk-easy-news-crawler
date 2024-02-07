# -*- encoding: utf-8 -*-
"""
@File:
    config.py
@Time:
    2024/02/06 11:53:38
@Author:
    Kevin Wang
@Desc:
    None
"""

from pathlib import Path

import yaml

module_folder_path = Path(__file__).resolve().parent
# config_path = module_folder_path.joinpath('configs', 'config.yaml')

# if config_path.is_file():
#     with open(config_path, 'r', encoding="utf-8") as file:
#         data_loaded = yaml.safe_load(file)
# else:
#     raise FileNotFoundError(f"No config.yaml found, please check that the file has been placed at {config_path}")

def path_decider(path):
    """若是 path 相對路徑，則回傳專案資料夾路徑 + path；若是絕對路徑則直接回傳。
    """
    path = Path(path).resolve()
    if path.is_absolute():
        return path
    return module_folder_path.joinpath(path)

package_path = Path(__file__).resolve().parents[1]
class ProjectConfigs:
    """此專案的一些共同設定值
    """
    PROJECT_PATH = package_path

    RAW_DIR = package_path.joinpath("data/raw")
    INTERIM_DIR = package_path.joinpath("data/interim")
    PROCESSED_DIR = package_path.joinpath("data/processed")

