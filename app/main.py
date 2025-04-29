from fastapi import FastAPI
from app.api.v1.route_example import router as example_router

app = FastAPI()

# 把 v1 版的 API router 掛進來
app.include_router(example_router, prefix="/api/v1", tags=["Example"])
