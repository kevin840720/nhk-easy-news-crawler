# nhk_easy_news_crawler

NHK 簡易新聞爬蟲：<https://www3.nhk.or.jp/news/easy/>

## 開發環境安裝

1. 安裝 pipenv
2. 複製 `.env.example` 為 `.env`，編輯連線參數（詳見「重要參數文件說明」）
3. 安裝依賴  

   ```bash
   pipenv install
   ```

4. 啟動服務  

   ```bash
   pipenv run python src/app.py
   ```

5. 確認服務啟動：<http://localhost:${SERVICE_PORT}/status>（預設 port 為 41260）

## 正式環境部署

1. 匯出 requirements.txt  

   ```bash
   pipenv requirements > requirements.txt
   ```

2. 建置映像  

   ```bash
   docker compose build --no-cache
   ```

3. 啟動容器  

   ```bash
   docker compose up -d
   ```

## 使用方式

### 1. 直接執行爬蟲

自動爬取 NHK 簡易新聞並匯入資料庫：

```bash
pipenv run python src/main.py
```

### 2. 透過 Flask API 啟動服務

啟動 Flask 伺服器：

```bash
pipenv run python src/app.py
```

伺服器啟動後，預設監聽於 `http://0.0.0.0:41260/`。

#### API 說明

- **GET /status**  
  服務存活檢查，回傳 `{"status": "ok"}`

- **GET /crawler/easy**  
  取得 NHK Easy News 資料，可選 query string `start_date`、`end_date`。

- **GET /crawler/news**  
  取得 NHK News 資料，可選 query string `start_date`、`end_date`。

範例：

```bash
curl "http://localhost:41260/crawler/easy?start_date=2024-06-01&end_date=2024-06-15"
```

回傳 JSON 範例：

```json
{
  "status": "success",
  "count": 10,
  "data": [...]
}
```

## 重要參數文件說明

### .env

`.env` 會同時被主程式（Python）和 docker-compose.yaml 使用。

- `PG_DBNAME`：PostgreSQL 資料庫名稱  
- `PG_USERNAME`：PostgreSQL 使用者名稱  
- `PG_PASSWORD`：PostgreSQL 密碼  
- `PG_PORT`：PostgreSQL 對外連接的主機 port（例如 11624）  
- `SERVICE_PORT`：Flask 服務對外 port（預設 41260）  
- `CONTAINER_NAME`：PostgreSQL 容器名稱  

### docker-compose.yaml

- 管理所有服務容器的設定。
- 常用端口與連線關係如下（已在檔案內部以註解標明）：

  | 來源           | 目標           | 通訊方式                    | 說明                                  |
  |----------------|----------------|-----------------------------|---------------------------------------|
  | 主機           | PostgreSQL     | `${PG_PORT}` → `5432`           | 本機可連 pgAdmin/CLI                  |
  | 主機           | NHK Crawler    | `${SERVICE_PORT}` → `${SERVICE_PORT}` | API 對外服務                    |
  | NHK Crawler    | PostgreSQL     | `japanese_article_postgresql:5432` | container 內部直連資料庫       |

### Dockerfile

- 建置 NHK Crawler 專用的 Python 執行環境。

### database/docker-compose-yaml 說明

- 此檔案為**開發用**的 docker-compose 設定檔，目的是**臨時建立本地 PostgreSQL**。
- 常用於本機端測試或開發，不影響正式資料庫。
- 預設將資料儲存於 `database/data` 目錄下，方便資料持久化與備份。
- 需搭配專案根目錄下的 `.env` 檔案設定連線參數。
- 由於只啟動資料庫服務，適合快速拉起本地 DB，供測試或本地開發使用。

## 刪除所有容器與資料

```bash
docker compose down -v
```

## 專案架構

```txt
.
├── CHANGELOG.md                 # 更新紀錄
├── conftest.py                  # 測試設定
├── database
│   └── docker-compose.yaml.example # 開發用本地資料庫 docker compose 範例
├── docker-compose.yaml          # 專案主 docker compose 配置
├── Dockerfile                   # Python/爬蟲服務的 Docker 建置腳本
├── Pipfile                      # pipenv 依賴管理檔
├── Pipfile.lock                 # pipenv 鎖定依賴版本
├── README.md                    # 專案說明文件
├── requirements.txt             # requirements 格式依賴清單
├── src
│   ├── app.py                   # Flask API 主程式
│   ├── config.py                # 設定參數相關
│   ├── crawler.py               # 爬蟲實作
│   ├── export.py                # 匯出資料工具
│   ├── __init__.py              # 專案模組化
│   ├── main.py                  # 指令列爬蟲主程式
│   ├── objects.py               # 物件結構定義
│   ├── parser.py                # 解析網頁用
│   └── utils.py                 # 共用工具
├── test_environment.py          # 測試環境驗證
├── tests
│   ├── test_parser.py           # parser 單元測試
│   └── test_utils.py            # utils 單元測試
└── __version__.py               # 專案版本資訊
```
