from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from src import schemas
from src.services import sse_service
from typing import Callable, AsyncGenerator
import asyncio
import logging
import json

router = APIRouter()
logger = logging.getLogger(__name__)

def get_error_message(character_type: int) -> dict:
    if character_type == 0:
        return {
            "type": "model_output",
            "contents": "앗 미안해.. 서버에 문제가 발생한 것 같아. 다시 한 번만 더 물어봐줄 수 있을까?",
            "verbose": "에러가 발생하여 이를 알리는 채팅 응답 발송"
        }
    elif character_type == 1:
        return {
            "type": "model_output",
            "contents": "헉!!! 미안해!! 서버에 문제가 발생한 것 같아!! 다시 한 번만 더 물어봐줄래?!!",
            "verbose": "에러가 발생하여 이를 알리는 채팅 응답 발송"
        }
    else:
        return {
            "type": "model_output",
            "contents": "허엄.... 서버 장치에 문제가 발생한 듯 하오.... 미안하네만 한 번 더 물어봐 줄 수 있나...?",
            "verbose": "에러가 발생하여 이를 알리는 채팅 응답 발송"
        }

@router.get("", status_code=200)
async def sse_endpoint(
    code: str = Query(..., description="sse request hash value"),
    service: Callable[[str], AsyncGenerator[str, None]] = Depends(sse_service.service)
):
    async def event_generator(code: str):
        stop_signal = {
            "type": "signal",
            "contents": "finish",
            "verbose": "스트리밍 세션 종료 및 SSE 종료"
        }

        character_type = int(code[-1])

        try:
            logger.info(f"SSE 스트림 시작: code={code}")
            async for message in service(code):
                yield f"data: {message}\n\n"

        except HTTPException as he:
            logger.error(f"HTTPException 발생: {he.detail}")
            error_message = get_error_message(character_type)
            yield f"event: error\ndata: {json.dumps(error_message, ensure_ascii=False)}\n\n"

        except asyncio.CancelledError:
            logger.warning("클라이언트 연결 취소")
            error_message = get_error_message(character_type)
            yield f"event: error\ndata: {json.dumps(error_message, ensure_ascii=False)}\n\n"

        except Exception as e:
            logger.exception(f"예기치 않은 에러 발생: {str(e)}")
            error_message = get_error_message(character_type)
            yield f"event: error\ndata: {json.dumps(error_message, ensure_ascii=False)}\n\n"

        finally:
            logger.info(f"SSE 스트림 종료: code={code}")
            yield f"event: signal\ndata: {json.dumps(stop_signal, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_generator(code), media_type="text/event-stream")
