FROM python:3.11
WORKDIR /src

# 安裝依賴
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 複製程式碼
COPY src/ .

# 定義並使用 PORT
ARG PORT=5000
ENV PORT=${PORT}

EXPOSE ${PORT}

CMD ["python", "app.py"]
