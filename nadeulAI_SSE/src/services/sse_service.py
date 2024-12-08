import asyncio
import redis.asyncio as aioredis
import logging
import json
from nadeulAI_SSE.src import schemas
from nadeulAI_SSE.src.constants.signals import START_SIGNAL
from confidential.constants import REDIS_HOST, REDIS_PORT, AI_SERVER_BASE_URL
from pathlib import Path
from fastapi import HTTPException
from httpx import AsyncClient, TimeoutException


async def service(hash: str):
    machine_idx = int(hash[:2])

    r_lb = aioredis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
    r_schedule = aioredis.Redis(
        host=REDIS_HOST, port=REDIS_PORT, db=1, decode_responses=True
    )
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)

    assigned_transformed_str = await r_schedule.get(hash)
    if not assigned_transformed_str:
        raise KeyError(f"Hash {hash} not found in Redis")

    assigned_transformed_dto = schemas.AssignTransformedDTO(
        **json.loads(assigned_transformed_str)
    )

    await r_schedule.delete(hash, assigned_transformed_str)
    asyncio.create_task(r_lb.set(f"ai_server_is_busy_{machine_idx}", 1, ex=40))

    try:
        async with AsyncClient(
            base_url=AI_SERVER_BASE_URL.format(str(machine_idx))
        ) as async_client:
            async with async_client.stream(
                "POST", "/", json={**assigned_transformed_dto.model_dump()}, timeout=40
            ) as response:
                result_text = ""
                is_first = True

                async for chunk in response.aiter_text():
                    if is_first:
                        yield START_SIGNAL
                        is_first = False
                    result_text += chunk.replace("'", "").replace('"', "")
                    result_text.replace("[말투반영]", "")
                    model_output = schemas.Signal(
                        type="model_output",
                        contents=result_text,
                        verbose="질문에 대한 모델 출력입니다.",
                    )

                    yield model_output

                if is_first:
                    yield "No Response"

    except TimeoutException:
        yield "No Response"

    finally:
        await r_lb.delete(f"ai_server_is_busy_{machine_idx}")
        await r_schedule.close()
        await r_lb.close()
