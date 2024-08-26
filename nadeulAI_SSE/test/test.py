from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import time
import asyncio
import json

app = FastAPI()

dummy_data = [{"type": "model_output", "contents": "수원", "verbose": "질문에 대한 모델 출력입니다."},
              {"type": "model_output", "contents": "수원 화성에",
                  "verbose": "질문에 대한 모델 출력입니다."},
              {"type": "model_output", "contents": "수원 화성에 오신",
                  "verbose": "질문에 대한 모델 출력입니다."},
              {"type": "model_output", "contents": "수원 화성에 오신 것을",
                  "verbose": "질문에 대한 모델 출력입니다."},
              {"type": "model_output", "contents": "수원 화성에 오신 것을 환영합니다.", "verbose": "질문에 대한 모델 출력입니다."}]


async def event_stream():
    url_connected_signal = {"type": "signal", "contents": "url_connected",
                            "verbose": "Spring 서버에서 받은 URL과 연결됨, SSE 연결 시작"}
    yield json.dumps(url_connected_signal, ensure_ascii=False) + "\n"
    await asyncio.sleep(3)

    start_signal = {"type": "signal", "contents": "start",
                    "verbose": "내 차례가 되어 AI 모델과 스트리밍 세션이 연결됨, 로딩 뷰 종료"}
    yield json.dumps(start_signal, ensure_ascii=False) + "\n"
    await asyncio.sleep(0.1)

    for item in dummy_data:
        yield json.dumps(item, ensure_ascii=False) + "\n"
        await asyncio.sleep(0.1)

    stop_signal = {"type": "signal", "contents": "finish",
                   "verbose": "AI 모델이 Output을 전부 다 보냄, 스트리밍 세션 종료 및 SSE 종료"}
    yield json.dumps(stop_signal, ensure_ascii=False)


@app.get("/sse", description="""SSE 통신은 String 전달만 가능하므로 (type, contents, verbose) 값이 stringify 된 json 형태로 전달됩니다.
Ex. {"type": "model_output", "contents": "수원", "verbose": "질문에 대한 모델 출력입니다."}""")
async def sse_endpoint():
    return StreamingResponse(event_stream(), media_type="text/event-stream")
