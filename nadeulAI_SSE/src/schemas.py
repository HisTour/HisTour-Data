from pydantic import BaseModel, field_validator
from fastapi import HTTPException
from typing import List

class AssignRequest(BaseModel):
    character: int
    QA: List[str]
    mission_name: str
    submission_name: str
    task_sequence: int

    @field_validator('QA')
    def check_item_length(cls, v):
        if len(v) % 2 == 0:
            raise ValueError("The length of QA List must be odd, not even.")
        return v

class AssignData(BaseModel):
    url: str

class AssignResponse(BaseModel):
    data: AssignData



