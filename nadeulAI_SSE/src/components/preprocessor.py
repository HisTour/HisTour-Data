from nadeulAI_SSE.src import schemas
from typing import List, Dict
from fastapi import HTTPException
import sqlite3
class Preprocessor():
    def __init__(self, db_path: str, top_k: int = 3) -> None:
        self.db_path = db_path
        self.top_k = top_k

    def transform(self, request: schemas.AssignRequest) -> schemas.AssignTransformedDTO:
        result = dict()
        result["QA"] = request.QA
        result["candidates"] = self._get_candidates(self.db_path,
                                                   request.mission_name,
                                                   request.submission_name,
                                                   request.task_sequence)
        result["top_k"] = self.top_k
        result["character_type"] = request.character

        result = schemas.AssignTransformedDTO(**result)
        
        return result
    
    def _get_candidates(self, db_path: str,
                       mission_name: str,
                       submission_name: str,
                       task_sequence:str) -> List[str]:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            query = (
                "SELECT * FROM knowledges "
                "WHERE mission_name = ? AND "
                "submission_name = ? AND "
                "task_sequence = ?"
            )
            cursor.execute(query, (mission_name, submission_name, task_sequence))
            rows = cursor.fetchall()

        candidate_sentences = []
        if len(rows) == 0:
            raise HTTPException(status_code=422, detail="Invalid Task Info (mission_name, submission_name, task_sequence)")
            
        for row in rows:
            document = row[4]
            candidate_sentences += list(document.split(".")[:-1])

        return candidate_sentences        