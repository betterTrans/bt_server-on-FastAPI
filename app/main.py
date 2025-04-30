from fastapi import FastAPI
from app.api.v1 import router as api_v1_router
from dotenv import load_dotenv

load_dotenv() # 從 .env 載入環境變數

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World"}

# 把 v1 版的所有 API router 自動掛進來
app.include_router(api_v1_router, prefix="/api")
