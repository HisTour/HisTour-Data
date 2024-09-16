import redis.asyncio as aioredis
from confidential.constants import REDIS_HOST, REDIS_PORT, AI_SERVER_COUNT
from nadeulAI_SSE.src import schemas
import uuid
import json
import asyncio

class Scheduler():
    r_lb = None
    r_schedule = None
    lock = asyncio.Lock()

    @staticmethod
    async def initialize() -> None:
        Scheduler.r_lb = aioredis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
        Scheduler.r_schedule = aioredis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=1, decode_responses=True)

        await Scheduler.r_lb.flushdb()
        await Scheduler.r_schedule.flushdb()
        await Scheduler.r_lb.set("current_ai_server_idx", -1)
        for _ in range(AI_SERVER_COUNT):
            await Scheduler.r_lb.rpush("ai_server_is_busy", 0)

    @staticmethod
    async def scheduling(assigned_transformed_dto: schemas.AssignTransformedDTO) -> str:
        async with Scheduler.lock:
            current_ai_server_idx = int(await Scheduler.r_lb.get("current_ai_server_idx"))
            current_ai_server_idx = (current_ai_server_idx + 1) % AI_SERVER_COUNT
            await Scheduler.r_lb.set("current_ai_server_idx", current_ai_server_idx)

            while True:
                if int(await Scheduler.r_lb.lindex("ai_server_is_busy", current_ai_server_idx)):
                    pass
                else:
                    hash_id = Scheduler.make_hash(current_ai_server_idx, assigned_transformed_dto.character_type)
                    await Scheduler.r_schedule.set(hash_id, json.dumps(assigned_transformed_dto.model_dump(), ensure_ascii=False))
                    await Scheduler.r_lb.lset("ai_server_is_busy", current_ai_server_idx, 1)
                    return hash_id

    @staticmethod
    def make_hash(assigned_machine: int, character_type: int) -> str:
        random_uuid = uuid.uuid4().hex
        hash_id = f"{str(assigned_machine).zfill(2)}{random_uuid[:12]}{character_type}"
        return hash_id
    
    @staticmethod
    async def close() -> None:
        await Scheduler.r_lb.close()
        await Scheduler.r_schedule.close()
