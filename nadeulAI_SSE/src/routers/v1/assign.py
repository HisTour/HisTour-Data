import logging
from fastapi import APIRouter, Depends, HTTPException
from nadeulAI_SSE.src import schemas
from nadeulAI_SSE.src.services import assign_service
from typing import Callable
import time
router = APIRouter()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) 

@router.post("", response_model=schemas.AssignResponse, status_code=201)
async def assign_endpoint(request: schemas.AssignRequest):
    url = await assign_service.service(request)
    return schemas.AssignResponse(data=schemas.AssignData(url=url))
    
    
    
