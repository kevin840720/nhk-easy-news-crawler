# -*- encoding: utf-8 -*-
"""
@File    :  main.py
@Time    :  2024/02/06 13:44:39
@Author  :  Kevin Wang
@Desc    :  None
"""
from utils import NHKEasyNewsClient

# a = NHKEasyNewsClient().get_news_summary()
# print(a.popitem())
import m3u8
playlist = m3u8.load('https://vod-stream.nhk.jp/news/easy_audio/ne2024120311060_uyMAQIva7dGCGgevzzpy34wZx17ZH5oCVYydZu66/index.m3u8')  # this could also be an absolute filename

from pprint import pprint

# pprint(playlist.files)
# pprint(playlist.playlists[0].__dict__)



playlist = m3u8.load('https://vod-stream.nhk.jp/news/easy_audio/ne2024120312204_ndx8wGNRY3nFMtQW9m7Iy4G0JbD416rDvXL4Tk7p/index_64k.m3u8?aka_me_session_id=AAAAAAAAAAAXZlFnAAAAAHguuYCvq46C0h7tzCQBX7yN5zAvsGhRmEwX3p8%2f7d+yaysJDFbSYAyicETv0CuQBIIYnwLZtAUa&aka_media_format_type=hls')  # this could also be an absolute filename
# # pprint(playlist.playlists)
pprint(playlist.keys[0].__dict__)

# playlist = m3u8.load('https://vod-stream.nhk.jp/news/easy_audio/ne2024120312204_ndx8wGNRY3nFMtQW9m7Iy4G0JbD416rDvXL4Tk7p/index_64k_00001.aac?aka_me_session_id=AAAAAAAAAAAXZlFnAAAAAHguuYCvq46C0h7tzCQBX7yN5zAvsGhRmEwX3p8%2f7d+yaysJDFbSYAyicETv0CuQBIIYnwLZtAUa&aka_msn=1&aka_hls_version=3&aka_media_format_type=hls')  # this could also be an absolute filename
# pprint(playlist.segments[0])

# from Crypto.Cipher import AES


# # AES-128 解密
# def decrypt_segment(segment_data, key):
#     cipher = AES.new(key, AES.MODE_CBC, iv=b'\x00' * 16)  # 初始化向量通常為零
#     return cipher.decrypt(segment_data)

# # 加密片段 URL
# encrypted_segment_url = "https://vod-stream.nhk.jp/news/easy_audio/.../segment.aac"
# segment_response = requests.get(encrypted_segment_url)

# if segment_response.status_code == 200:
#     encrypted_data = segment_response.content
#     decrypted_data = decrypt_segment(encrypted_data, key)

#     # 將解密後的片段保存到文件
#     with open("decrypted_segment.aac", "wb") as f:
#         f.write(decrypted_data)
#     print("Segment decrypted successfully!")
# else:
#     raise Exception(f"Failed to fetch encrypted segment: {segment_response.status_code}")