import logging
from fastapi import APIRouter, Depends, HTTPException
from nadeulAI_SSE.src import schemas
from nadeulAI_SSE.src.services import assign_service
from typing import Callable

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("", response_model=schemas.AssignResponse, status_code=201)
def assign_endpoint(request: schemas.AssignRequest, 
                    service: Callable[[schemas.AssignRequest], str] = Depends(assign_service.service)):
    try:
        url = service(request)
        return schemas.AssignResponse(data=schemas.AssignData(url=url))
    
    except ValueError as e:
        logger.warning(f"ValueError occurred for request {request}: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Bad Request: {str(e)}")
    
    except Exception as e:
        logger.error(f"Unhandled exception for request {request.dict()}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
