# -*- encoding: utf-8 -*-
"""
@File    :  export.py
@Time    :  2024/11/10 16:13:34
@Author  :  Kevin Wang
@Desc    :  Collect method which export to 
"""

from typing import (Any,
                    Iterable,
                    Optional,
                    )
import json
import os

from dotenv import load_dotenv
from psycopg2.extras import execute_batch
import psycopg2

from objects import News, Media, HTMLContent

load_dotenv()

class Export2PostgreSQL:
    """控制 PostgreSQL 輸出"""
    def __init__(self, **kwargs) -> None:
        # 建立資料庫連線
        self.conn = psycopg2.connect(dbname=os.getenv("PG_DBNAME"),
                                     user=os.getenv("PG_USERNAME"),
                                     password=os.getenv("PG_PASSWORD"),
                                     host=os.getenv("PG_HOST") or "localhost",
                                     port=os.getenv("PG_PORT"),
                                     )
        self.cursor = self.conn.cursor()

        # 設定 schema 和 table 名稱
        self.schema = kwargs.get("schema", "japanese_news")
        self.news_table = kwargs.get("news_table", "news")
        self.media_table = kwargs.get("media_table", "media")
        self.html_content_table = kwargs.get("html_content_table", "html_contents")

        # SQL 緩存
        self.sql_cache = []

        # 初始化資料庫結構
        self._initialize()

    def _initialize(self):
        """初始化資料庫結構，建立 schema 和 tables"""
        # 建立 schema 的 SQL 語句
        create_schema_sql = f"CREATE SCHEMA IF NOT EXISTS \"{self.schema}\";"

        # 建立 media 表的 SQL 語句
        create_media_table_sql = f"""
        CREATE TABLE IF NOT EXISTS \"{self.schema}\".\"{self.media_table}\" (
            id VARCHAR(127) PRIMARY KEY,
            status INT,
            type VARCHAR(20) CHECK (type IN ('Audio', 'Video')),
            url VARCHAR(511),
            filepath VARCHAR(511),
            publication_time TIMESTAMP,
            download_time TIMESTAMP
        );
        """

        # 建立 html_content 表的 SQL 語句
        create_html_content_table_sql = f"""
        CREATE TABLE IF NOT EXISTS \"{self.schema}\".\"{self.html_content_table}\" (
            id VARCHAR(127) PRIMARY KEY,
            status INT,
            url VARCHAR(511),
            filepath VARCHAR(511),
            title VARCHAR(255),
            article TEXT,
            publication_time TIMESTAMP,
            download_time TIMESTAMP
        );
        """

        # 建立 news 表的 SQL 語句，並設定外鍵關聯到 media, html_content
        create_news_table_sql = f"""
        CREATE TABLE IF NOT EXISTS \"{self.schema}\".\"{self.news_table}\" (
            id VARCHAR(127) PRIMARY KEY,
            source VARCHAR(255),
            source_id VARCHAR(255),
            title VARCHAR(255),
            url VARCHAR(511),
            publication_time TIMESTAMP,
            download_time TIMESTAMP,
            author TEXT,
            media_id VARCHAR(127),
            html_content_id VARCHAR(127),
            FOREIGN KEY (media_id) REFERENCES \"{self.schema}\".\"{self.media_table}\"(id) ON DELETE CASCADE,
            FOREIGN KEY (html_content_id) REFERENCES \"{self.schema}\".\"{self.html_content_table}\"(id) ON DELETE CASCADE
        );
        """

        # 執行 SQL 語句以創建 schema 和 tables
        self.cursor.execute(create_schema_sql)
        self.cursor.execute(create_media_table_sql)
        self.cursor.execute(create_html_content_table_sql)
        self.cursor.execute(create_news_table_sql)
        self.conn.commit()

    def _insert_to_news_table(self,
                              obj:News,
                              schema:str,
                              table:str,
                              ) -> tuple:
        """生成插入 News 資料的 SQL 字串與對應的值"""

        sql = f"""
        INSERT INTO "{schema}"."{table}"
        (id, source, source_id, title, url, publication_time, download_time, author, media_id, html_content_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id)
        DO UPDATE SET
            source = EXCLUDED.source,
            source_id = EXCLUDED.source_id,
            title = EXCLUDED.title,
            url = EXCLUDED.url,
            publication_time = EXCLUDED.publication_time,
            download_time = EXCLUDED.download_time,
            author = EXCLUDED.author,
            media_id = EXCLUDED.media_id,
            html_content_id = EXCLUDED.html_content_id;
        """

        values = (
            str(obj.id),  # 將 int 轉為字串以符合 VARCHAR(50) 的定義
            obj.source,
            obj.source_id,
            obj.title,
            obj.url,
            obj.publication_time,
            obj.download_time,
            obj.author,
            obj.media.id if obj.media else None,
            obj.html_content.id if obj.html_content else None,
        )

        self.sql_cache.append((sql, values))
        return sql, values

    def _insert_to_media_table(self,
                               obj:Media,
                               schema:str,
                               table:str,
                               ) -> tuple:
        """生成插入 Media 資料的 SQL 字串與對應的值"""
        sql = f"""
        INSERT INTO "{schema}"."{table}"
        (id, status, type, url, filepath, publication_time, download_time)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id)
        DO UPDATE SET
            status = EXCLUDED.status,
            type = EXCLUDED.type,
            url = EXCLUDED.url,
            filepath = EXCLUDED.filepath,
            publication_time = EXCLUDED.publication_time,
            download_time = EXCLUDED.download_time;
        """

        values = (
            obj.id,
            int(obj.status) if obj.status is not None else None,
            obj.type,
            obj.url,
            str(obj.filepath) if obj.filepath else None,
            obj.publication_time,
            obj.download_time,
        )

        self.sql_cache.append((sql, values))
        return sql, values

    def _insert_to_html_content_table(self,
                                      obj:HTMLContent,
                                      schema:str,
                                      table:str,
                                      ) -> tuple:
        """生成插入 HTMLContent 資料的 SQL 字串與對應的值"""
        sql = f"""
        INSERT INTO "{schema}"."{table}"
        (id, status, url, filepath, title, article, publication_time, download_time)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id)
        DO UPDATE SET
            status = EXCLUDED.status,
            url = EXCLUDED.url,
            filepath = EXCLUDED.filepath,
            title = EXCLUDED.title,
            article = EXCLUDED.article,
            publication_time = EXCLUDED.publication_time,
            download_time = EXCLUDED.download_time;
        """

        values = (
            obj.id,
            int(obj.status) if obj.status is not None else None,
            obj.url,
            str(obj.filepath) if obj.filepath else None,
            obj.title,
            obj.article,
            obj.publication_time,
            obj.download_time,
        )

        self.sql_cache.append((sql, values))
        return sql, values

    def _run_sql(self) -> None:
        """執行緩存中的 SQL 語句，依據 SQL 語句的相似性選擇批次執行或單次執行，並保持執行順序。
        """
        batch_group = []
        current_sql = None

        for sql, value in self.sql_cache:
            # 檢查是否與前一條 SQL 相同
            if sql == current_sql:
                batch_group.append(value)
            else:
                # 如果有累積的批次組，就執行批次操作
                if batch_group:
                    try:
                        execute_batch(self.cursor, current_sql, batch_group)
                        self.conn.commit()
                    except psycopg2.DatabaseError as err:
                        # 發生資料庫錯誤時進行回滾，以撤銷當前交易的所有變更，確保資料庫的一致性
                        self.conn.rollback()
                        print(f"""Database error during batch execution: {err}. Rolled back transaction.
                              follwing SQL not performed: {current_sql}, {batch_group}""")
                    finally:
                        batch_group = []

                # 更新當前 SQL 並加入第一個值
                current_sql = sql
                batch_group = [value]

        # 處理最後一組批次操作
        if batch_group:
            try:
                execute_batch(self.cursor, current_sql, batch_group)
                self.conn.commit()
            except psycopg2.DatabaseError as err:
                self.conn.rollback()
                print(f"Database error during batch execution: {err}. Rolled back transaction.")

        # 清空 SQL 快取
        self.sql_cache.clear()

    def insert(self, obj:News):
        """..."""
        if obj.media:
            self._insert_to_media_table(obj.media,
                                        self.schema,
                                        self.media_table,
                                        )
        if obj.html_content:
            self._insert_to_html_content_table(obj.html_content,
                                               self.schema,
                                               self.html_content_table,
                                               )
        
        # 有 Foreign Key 的 Table 要最後插入
        self._insert_to_news_table(obj,
                                   self.schema,
                                   self.news_table,
                                   )
        self._run_sql()


Export2PostgreSQL()