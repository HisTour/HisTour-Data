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
    def check_qa_length(cls, v):
        if len(v) % 2 == 0:
            raise ValueError("The length of QA List must be odd, not even.")
        return v
    
    @field_validator('character')
    def check_character_type(cls, v):
        if v not in [0, 1, 2]:
            raise ValueError("Invalid Character Type")
        return v


class AssignData(BaseModel):
    url: str

class AssignResponse(BaseModel):
    data: AssignData


class AssignTransformedDTO(BaseModel):
    character_type: int
    QA: List[str]
    candidates: List[str]
    top_k: int
    
    


