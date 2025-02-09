from nadeulAI_SSE.src import schemas
from typing import List, Dict, Any, Optional
from fastapi import HTTPException

import sqlite3
import chromadb


class Preprocessor:
    def __init__(self, vector_db_path: str, top_k: int = 3) -> None:
        self.vector_db_path = vector_db_path
        self.top_k = top_k

    def transform(self, request: schemas.AssignRequest) -> schemas.AssignTransformedDTO:
        result = dict()
        result["QA"] = request.QA

        if len(result["QA"]) >= 5:
            result["QA"] = result["QA"][-5:]

        result["rag_results"] = self._get_rag_results(
            result["QA"],
            request.mission_name,
            request.submission_name,
            request.task_sequence,
        )
        result["top_k"] = self.top_k
        result["character_type"] = request.character

        result = schemas.AssignTransformedDTO(**result)

        return result

    def _get_rag_results(
        self,
        query_text_list: List[str],
        mission_name: str,
        submission_name: str,
        task_sequence: str,
    ) -> List[str]:
        result_set = set()
        for query_text in query_text_list:
            result_set.update(
                self._query_similar_docs(
                    query_text,
                    metadata_filter={
                        "mission_name": mission_name,
                        "submission_name": submission_name,
                        "task_sequence": task_sequence,
                    },
                    n_results=self.top_k,
                )
            )

        return list(result_set)

    def _query_similar_docs(
        self,
        query_text: str,
        metadata_filter: Optional[Dict[str, Any]] = None,
        n_results: int = 3,
    ) -> List[Dict[str, Any]]:

        client = chromadb.PersistentClient(path=self.vector_db_path)
        collection = client.get_collection(name="knowledge_base")

        where_condition = None
        if metadata_filter:
            where_condition = {
                "$and": [{key: value} for key, value in metadata_filter.items()]
            }

        results = collection.query(
            query_texts=[query_text],
            where=where_condition,
            n_results=n_results,
            include=["documents"],
        )

        formatted_results = []

        for doc in results["documents"][0]:
            formatted_results.append(doc)

        return formatted_results

    def _get_candidates(
        self, db_path: str, mission_name: str, submission_name: str, task_sequence: str
    ) -> List[str]:
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
            raise HTTPException(
                status_code=422,
                detail="Invalid Task Info (mission_name, submission_name, task_sequence)",
            )

        for row in rows:
            document = row[4]
            candidate_sentences += list(document.split(".")[:-1])

        candidate_sentences = [s for s in candidate_sentences if len(s) > 5]

        return candidate_sentences
