from fastapi import FastAPI
from nadeulAI_SSE.src.routers.v1 import assign, sse

app = FastAPI(docs_url="/docs", openapi_url="/open-api-docs")

app.include_router(assign.router, prefix="/assign")
# app.include_router(sse.router, prefix="/sse")


