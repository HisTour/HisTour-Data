from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from nadeulAI_SSE.src import schemas
from nadeulAI_SSE.src.services import sse_service
from nadeulAI_SSE.src.constants.signals import *
from typing import List
from dataclasses import asdict
import asyncio
import logging
import json

router = APIRouter()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def generate_error_signal(character_type: int) -> dict:
    messages = {
        0: "앗 미안해.. 서버에 문제가 발생했거나, 이 미션 주제랑 너무 다른 질문을 한 것 같아. 다시 한 번만 더 물어봐줄 수 있을까?",
        1: "헉!!! 미안해!! 서버에 문제가 발생했거나 이 미션 주제랑 너무 다른 질문을 한 것 같아!!! 다시 한 번만 더 물어봐줄래?!!",
        2: "허엄.... 서버 장치에 문제가 발생했거나 이 미션 주제랑 너무 다른 질문을 한 듯 하오.... 미안하네만 한 번 더 물어봐 줄 수 있나...?",
    }
    return Signal(
        type="model_output",
        contents=messages.get(character_type),
        verbose="에러가 발생하여 이를 알리는 채팅 응답 발송",
    )


def send_signals_when_error_occurs(error_signal: Signal) -> List[dict]:
    return [
        f"data: {json.dumps(asdict(START_SIGNAL), ensure_ascii=False)}\n\n".replace(
            "'", '"'
        ),
        f"data: {json.dumps(asdict(error_signal), ensure_ascii=False)}\n\n".replace(
            "'", '"'
        ),
    ]


@router.get(
    "",
    status_code=200,
    description="클라이언트 측에서 제공받은 URL로 접근하는 API 입니다.",
)
async def sse_endpoint(hash: str = Query(..., description="sse request hash value")):
    async def event_generator(hash: str):
        character_type = int(hash[-1])
        error_signal = generate_error_signal(character_type)

        try:
            logger.info(f"SSE 스트림 시작: hash={hash}")
            yield f"data: {json.dumps(asdict(URL_CONNECTED_SIGNAL), ensure_ascii=False)}\n\n".replace(
                "'", '"'
            )
            async for message in sse_service.service(hash):
                if message != "No Response":
                    yield f"data: {json.dumps(asdict(message), ensure_ascii=False)}\n\n".replace(
                        "'", '"'
                    )
                else:
                    for wrapped_signal in send_signals_when_error_occurs(error_signal):
                        yield wrapped_signal

        except Exception as e:
            if isinstance(e, HTTPException):
                logger.error(f"HTTPException 발생: {e.detail}")

            elif isinstance(e, KeyError):
                logger.error(f"KeyError 발생: {str(e)} ")

            elif isinstance(e, asyncio.CancelledError):
                logger.warning("클라이언트 연결 취소")

            else:
                logger.exception(f"예기치 않은 에러 발생: {str(e)}")

            for signal in send_signals_when_error_occurs(error_signal):
                yield signal

        finally:
            logger.info(f"SSE 스트림 종료: hash={hash}")
            yield f"data: {json.dumps(asdict(STOP_SIGNAL), ensure_ascii=False)}\n\n".replace(
                "'", '"'
            )

    return StreamingResponse(event_generator(hash), media_type="text/event-stream")
