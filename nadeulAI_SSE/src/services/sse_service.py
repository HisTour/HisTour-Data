import asyncio
import redis.asyncio as aioredis
import logging
import json
from nadeulAI_SSE.src import schemas
from confidential.constants import REDIS_HOST, REDIS_PORT, AI_SERVER_BASE_URL
from pathlib import Path
from fastapi import HTTPException
from httpx import AsyncClient, TimeoutException


async def service(hash: str):
    machine_idx = int(hash[:2])

    r_lb = aioredis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
    r_schedule = aioredis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=1, decode_responses=True)
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)

    assigned_transformed_str = await r_schedule.get(hash)
    assigned_transformed_dto = schemas.AssignTransformedDTO(**json.loads(assigned_transformed_str))

    asyncio.create_task(r_schedule.set(hash, assigned_transformed_str, ex=40))
    asyncio.create_task(r_lb.set(f"ai_server_is_busy_{machine_idx}", 1, ex=40))

    try:
        async with AsyncClient(base_url=AI_SERVER_BASE_URL.format(str(machine_idx))) as async_client:
            async with async_client.stream(
                "GET", "/", params={**assigned_transformed_dto.model_dump()},
                timeout=40) as response:
                result_text = ""
                is_first = True
                start_signal = {"type": "signal", "contents": "start",
                        "verbose": "내 차례가 되어 AI 모델과 스트리밍 세션이 연결됨, 로딩 뷰 종료"}
                
                async for chunk in response.aiter_text():
                    if is_first:
                        yield start_signal
                        is_first = False
                    result_text += chunk
                    model_output = {"type": "model_output",
                                    "contents": result_text,
                                    "verbose": "질문에 대한 모델 출력입니다."}
                    
                    yield model_output

                if is_first:
                    yield "No Response"

    except TimeoutException:
        yield "No Response"

    finally:
        await r_schedule.delete(hash, assigned_transformed_str)
        await r_lb.delete(f"ai_server_is_busy_{machine_idx}")
        await r_schedule.close()
        await r_lb.close()

        










    



    


async def main():
    # 요청 생성
    request = schemas.AssignRequest(
        character=1,
        QA=["안녕하세요?", "반가워요", "잘지내요?"],
        mission_name="테스트용 미션 이름",
        submission_name="테스트용 서브 미션 이름",
        task_sequence=1
    )



if __name__ == "__main__":
    asyncio.run(main())
