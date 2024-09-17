import redis.asyncio as aioredis
import logging
from confidential.constants import REDIS_HOST, REDIS_PORT, AI_SERVER_COUNT
from nadeulAI_SSE.src import schemas
import uuid
import json
import asyncio

class Scheduler():
    r_lb = aioredis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
    r_schedule = aioredis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=1, decode_responses=True)
    lock = asyncio.Lock()
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)

    @staticmethod
    async def initialize() -> None:
        await Scheduler.r_lb.flushdb()
        await Scheduler.r_schedule.flushdb()
        await Scheduler.r_lb.set("current_ai_server_idx", -1)
        

    @staticmethod
    async def scheduling(assigned_transformed_dto: schemas.AssignTransformedDTO) -> str:
        async with Scheduler.lock:
            idx = 0
            busy_log_flag = False
            while True:
                current_ai_server_idx = int(await Scheduler.r_lb.get("current_ai_server_idx"))
                current_ai_server_idx = (current_ai_server_idx + 1) % AI_SERVER_COUNT
                await Scheduler.r_lb.set("current_ai_server_idx", current_ai_server_idx)

                if await Scheduler.r_lb.get(f"ai_server_is_busy_{current_ai_server_idx}") is not None:
                    pass
                else:
                    hash_id = Scheduler.make_hash(current_ai_server_idx, assigned_transformed_dto.character_type)
                    await Scheduler.r_schedule.set(hash_id, json.dumps(assigned_transformed_dto.model_dump(), ensure_ascii=False), ex=19)
                    await Scheduler.r_lb.set(f"ai_server_is_busy_{current_ai_server_idx}", 1, ex=20)
                    print(current_ai_server_idx)
                    return hash_id
                idx += 1
                if idx >= AI_SERVER_COUNT and not busy_log_flag:
                    Scheduler.logger.warning("AI Servers are busy")
                    busy_log_flag = True

    @staticmethod
    def make_hash(assigned_machine: int, character_type: int) -> str:
        random_uuid = uuid.uuid4().hex
        hash_id = f"{str(assigned_machine).zfill(2)}{random_uuid[:12]}{character_type}"
        return hash_id
    
    @staticmethod
    async def close() -> None:
        await Scheduler.r_lb.close()
        await Scheduler.r_schedule.close()
