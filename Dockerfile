# 用輕量版 Python
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 複製檔案到容器
COPY . /app

# 安裝必要套件
RUN pip install --no-cache-dir -r requirements.txt

# 啟動 FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--proxy-headers"]