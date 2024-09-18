from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from nadeulAI_SSE.src import schemas
from nadeulAI_SSE.src.services import sse_service
from typing import Callable, AsyncGenerator
import asyncio
import logging
import json

router = APIRouter()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def get_error_message(character_type: int) -> dict:
    if character_type == 0:
        return {
            "type": "model_output",
            "contents": "앗 미안해.. 서버에 문제가 발생했거나, 이 미션 주제랑 너무 다른 질문을 한 것 같아. 다시 한 번만 더 물어봐줄 수 있을까?",
            "verbose": "에러가 발생하여 이를 알리는 채팅 응답 발송"
        }
    elif character_type == 1:
        return {
            "type": "model_output",
            "contents": "헉!!! 미안해!! 서버에 문제가 발생했거나 이 미션 주제랑 너무 다른 질문을 한 것 같아!!! 다시 한 번만 더 물어봐줄래?!!",
            "verbose": "에러가 발생하여 이를 알리는 채팅 응답 발송"
        }
    else:
        return {
            "type": "model_output",
            "contents": "허엄.... 서버 장치에 문제가 발생했거나 이 미션 주제랑 너무 다른 질문을 한 듯 하오.... 미안하네만 한 번 더 물어봐 줄 수 있나...?",
            "verbose": "에러가 발생하여 이를 알리는 채팅 응답 발송"
        }

@router.get("", status_code=200, description="클라이언트 측에서 제공받은 URL로 접근하는 API 입니다.")
async def sse_endpoint(
    hash: str = Query(..., description="sse request hash value")):
    async def event_generator(hash: str):
        url_connected_signal = {"type": "signal", "contents": "url_connected",
                                "verbose": "Spring 서버에서 받은 URL과 연결됨, SSE 연결 시작"}

        start_signal = {"type": "signal", "contents": "start",
                        "verbose": "내 차례가 되어 AI 모델과 스트리밍 세션이 연결됨, 로딩 뷰 종료"}

        stop_signal = {
            "type": "signal",
            "contents": "finish",
            "verbose": "스트리밍 세션 종료 및 SSE 종료"
        }

        character_type = int(hash[-1])
        error_message = get_error_message(character_type)

        try:
            logger.info(f"SSE 스트림 시작: hash={hash}")
            yield f"data: {json.dumps(url_connected_signal, ensure_ascii=False)}\n\n".replace("'", '"')
            async for message in sse_service.service(hash):
                if message != "No Response":
                    yield f"data: {message}\n\n".replace("'", '"')
                else:
                    yield f"data: {start_signal}\n\n".replace("'", '"')
                    yield f"data: {json.dumps(error_message, ensure_ascii=False)}\n\n".replace("'", '"')


        except HTTPException as he:
            logger.error(f"HTTPException 발생: {he.detail}")
            yield f"data: {start_signal}\n\n".replace("'", '"')
            yield f"data: {json.dumps(error_message, ensure_ascii=False)}\n\n".replace("'", '"')

        except asyncio.CancelledError:
            logger.warning("클라이언트 연결 취소")
            yield f"data: {start_signal}\n\n".replace("'", '"')
            yield f"data: {json.dumps(error_message, ensure_ascii=False)}\n\n".replace("'", '"')

        except Exception as e:
            logger.exception(f"예기치 않은 에러 발생: {str(e)}")
            yield f"data: {start_signal}\n\n".replace("'", '"')
            yield f"data: {json.dumps(error_message, ensure_ascii=False)}\n\n".replace("'", '"')

        finally:
            logger.info(f"SSE 스트림 종료: hash={hash}")
            yield f"data: {json.dumps(stop_signal, ensure_ascii=False)}\n\n".replace("'", '"')

    return StreamingResponse(event_generator(hash), media_type="text/event-stream")
