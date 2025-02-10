from fastapi import FastAPI
from nadeulAI_SSE.src.routers.v1 import assign, sse
from nadeulAI_SSE.src.routers import test_sse
from nadeulAI_SSE.src.components.scheduler import Scheduler
from nadeulAI_SSE.src.components.awaker import Awaker
from nadeulAI_SSE.src.components.preprocessor import Preprocessor
from contextlib import asynccontextmanager
from pathlib import Path
import asyncio


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 앱이 시작될 때 실행할 코드
    print("앱이 시작됩니다.")
    # 초기화 로직 (예: DB 연결)

    await Scheduler.initialize()
    asyncio.create_task(Awaker.awaker_on())
    current_file = Path(__file__).resolve()
    src_root = current_file.parents[0]
    vector_db_path = str(src_root / "database" / "vector_db")
    Preprocessor.initialize(vector_db_path)

    yield  # 여기가 실제로 앱이 동작하는 시점입니다.

    # 앱이 종료될 때 실행할 코드
    print("앱이 종료됩니다.")
    # 정리 로직 (예: DB 연결 종료)


app = FastAPI(docs_url="/docs", openapi_url="/open-api-docs", lifespan=lifespan)


app.include_router(assign.router, prefix="/api/v1/assign")
app.include_router(sse.router, prefix="/api/v1/sse")
app.include_router(test_sse.router, prefix="/sse")
