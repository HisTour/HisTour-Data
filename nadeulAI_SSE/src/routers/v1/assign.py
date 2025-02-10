import logging
from fastapi import APIRouter, Depends, HTTPException
from nadeulAI_SSE.src import schemas
from nadeulAI_SSE.src.services import assign_service
from typing import Callable
import time

router = APIRouter()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@router.post(
    "",
    response_model=schemas.AssignResponse,
    status_code=201,
    description="Java Spring 서버가 URL을 요청하는 API 입니다.",
)
async def assign_endpoint(request: schemas.AssignRequest):
    start_time = time.time()
    url = await assign_service.service(request)

    print(f"Time taken: {time.time() - start_time} seconds")
    return schemas.AssignResponse(data=schemas.AssignData(url=url))
