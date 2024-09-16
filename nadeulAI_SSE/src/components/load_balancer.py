from confidential.constants import REDIS_HOST, REDIS_PORT, AI_SERVER_COUNT
from src import schemas
from src.components.executer import Executer
import redis
import uuid
import json
import asyncio

class LoadBalancer():
    r_lb = redis.Redis(host=REDIS_HOST,
                       port=REDIS_PORT,
                       db=0,
                       decode_responses=True)
    
    r_schedule = redis.Redis(host=REDIS_HOST,
                       port=REDIS_PORT,
                       db=1,
                       decode_responses=True)
    
    lock = asyncio.Lock()

    # Initialize Redis Values
    @staticmethod
    async def initialize():
        await LoadBalancer.r_lb.flushdb()
        await LoadBalancer.r_schedule.flushdb()
        await LoadBalancer.r_lb.set("current_ai_server_idx", -1)
        for _ in range(AI_SERVER_COUNT):
            await LoadBalancer.r_lb.rpush("ai_server_is_busy", 0)
    
    

    @staticmethod
    async def load_balancing(assigned_transformed_dto:schemas.AssignedTransformedDTO) -> str:
        async with LoadBalancer.lock:
            current_ai_server_idx = await int(LoadBalancer.r_lb.get("current_ai_server_idx"))
            current_ai_server_idx = (current_ai_server_idx + 1) % AI_SERVER_COUNT
            await LoadBalancer.r_lb.set("current_ai_server_idx", current_ai_server_idx)

            while True:
                if int(LoadBalancer.r_lb.lindex("ai_server_is_busy", current_ai_server_idx)):
                    pass

                else:
                    hash_id = LoadBalancer.make_hash(current_ai_server_idx, assigned_transformed_dto.character_type)
                    await LoadBalancer.r_schedule.set(hash_id, json.dumps(assigned_transformed_dto, ensure_ascii=False))
                    await Executer.register(hash_id, assigned_transformed_dto)
                    await LoadBalancer.r_lb.lset("ai_server_is_busy", current_ai_server_idx, 1)
                    return hash_id
                    


    # Hash ID의 맨 앞 두자리: 할당된 ai-server 번호, 맨 뒷자리: 캐릭터 번호
    @staticmethod
    def make_hash(assigned_machine: int, character_type: int) -> str:
        random_uuid = uuid.uuid4().hex
        hash_id = f"{str(assigned_machine).zfill(2)}{random_uuid[:12]}{character_type}"
        return hash_id


        
