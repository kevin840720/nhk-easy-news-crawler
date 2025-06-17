#!/bin/bash
set -e

# PostgreSQL 容器內的 postgres 預設 UID/GID
POSTGRES_UID=999
POSTGRES_GID=999

load_env() {
  if [ -f .env ]; then
    echo "📦 載入環境變數 .env"
    set -o allexport
    source .env
    set +o allexport
  else
    echo "❌ 找不到 .env 檔案"
    exit 1
  fi
}

prepare_postgres_dir() {
  echo "📁 建立 PostgreSQL 資料目錄..."
  mkdir -p "$PG_VOLUME"
  echo "🔐 設定 PostgreSQL 資料目錄權限為 $POSTGRES_UID:$POSTGRES_GID"
  sudo chown -R $POSTGRES_UID:$POSTGRES_GID "$PG_VOLUME"
  sudo chmod 700 "$PG_VOLUME"
}

start_services() {
  echo "🚀 啟動 docker compose（PostgreSQL + 自建服務）..."
  docker compose up -d
}

check_postgres() {
  echo "🔍 測試 PostgreSQL 連線..."
  if command -v psql &>/dev/null; then
    PGPASSWORD="$PG_PASSWORD" psql -h localhost -U "$PG_USERNAME" -p "$PG_PORT" -d "$PG_DBNAME" -c 'SELECT 1;' >/dev/null && \
      echo "✅ PostgreSQL 連線成功" || echo "❌ PostgreSQL 連線失敗"
  else
    echo "⚠️ 未安裝 psql，略過 PostgreSQL 測試"
  fi
}

# === 主流程開始前的選項判斷 ===
if [ "$1" == "--recreate" ]; then
  echo "🔁 重建容器（保留資料）..."
  docker compose down
  docker compose up -d --force-recreate
  exit 0
elif [ "$1" == "--remove-all" ]; then
  echo "🔥 刪除所有資料與 volume..."
  docker compose down -v
  sudo rm -rf "$PG_VOLUME"
  docker volume prune -f
  exit 0
fi


load_env
prepare_postgres_dir
start_services

echo "⏳ 等待 PostgreSQL 連線（最多 60 秒，每秒重試）..."
for i in {1..60}; do
  check_postgres && break
  echo "🔁 第 $i 秒：尚未就緒，繼續等待..."
  sleep 1
  if [ "$i" -eq 60 ]; then
    echo "❌ PostgreSQL 在 60 秒內無法連線，退出"
    exit 1
  fi
done

cd ..
echo "✅ PostgreSQL 與服務已啟動，資料目錄已設定權限"
