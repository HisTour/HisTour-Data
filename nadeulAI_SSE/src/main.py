from fastapi import FastAPI
from nadeulAI_SSE.src.routers.v1 import assign, sse
from nadeulAI_SSE.src.components.scheduler import Scheduler
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 앱이 시작될 때 실행할 코드
    print("앱이 시작됩니다.")
    # 초기화 로직 (예: DB 연결)

    await Scheduler.initialize()

    yield  # 여기가 실제로 앱이 동작하는 시점입니다.
    
    # 앱이 종료될 때 실행할 코드
    print("앱이 종료됩니다.")
    # 정리 로직 (예: DB 연결 종료)

app = FastAPI(docs_url="/docs", openapi_url="/open-api-docs", lifespan=lifespan)


app.include_router(assign.router, prefix="/assign")
app.include_router(sse.router, prefix="/sse")


