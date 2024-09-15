from src import schemas
from typing import List, Dict
from fastapi import HTTPException
import sqlite3
class Preprocessor():
    def __init__(self, db_path: str, top_k: int = 3) -> None:
        self.db_path = db_path
        self.top_k = top_k

    def transform(self, request: schemas.AssignRequest) -> Dict:
        result = dict()
        result["QA"] = request["QA"]
        result["candidates"] = self.get_candidates(self.db_path,
                                                   request["mission_name"],
                                                   request["submission_name"],
                                                   request["task_sequence"])
        result["top_k"] = self.top_k
        result["character_type"] = request["character"]
        
        return result
    
    def get_candidates(self, db_path: str,
                       mission_name: str,
                       submission_name: str,
                       task_sequence:str) -> List[str]:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            query = (
                "SELECT * FROM candidates "
                "WHERE mission_name = ? AND "
                "submission_name = ? AND "
                "task_sequence = ?"
            )
            cursor.execute(query, (mission_name, submission_name, task_sequence))
            rows = cursor.fetchall()

        candidates_sentences = [] 
        for row in rows:
            document = row[1]
            if document is None:
                raise HTTPException(status_code=422,
                                    detail="Invalid Task Info")
            candidate_sentences += document.split(".")[:-1]

        return candidates_sentences

        
        
        
        


        
        
        