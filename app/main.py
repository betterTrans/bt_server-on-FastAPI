from fastapi import FastAPI
from app.api.v1 import router as v1_router

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World"}

# 把 v1 版的 API router 掛進來
# app.include_router(example_router, prefix="/api/v1", tags=["Example"])
# 自動把所有的 v1 版 API router 掛進來
app.include_router(v1_router, prefix="/api/v1")