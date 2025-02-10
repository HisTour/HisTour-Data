from nadeulAI_SSE.src import schemas
from typing import List, Dict, Any, Optional
from fastapi import HTTPException

import sqlite3
import chromadb


class Preprocessor:
    vector_db_path = None
    top_k = None
    client = None
    collection = None

    @staticmethod
    def initialize(vector_db_path: str, top_k: int = 3) -> None:
        Preprocessor.vector_db_path = vector_db_path
        Preprocessor.top_k = top_k

        # 클라이언트 설정에 silent=True 추가
        Preprocessor.client = chromadb.PersistentClient(
            path=vector_db_path,
            settings=chromadb.Settings(anonymized_telemetry=False, is_persistent=True),
        )

        Preprocessor.collection = Preprocessor.client.get_or_create_collection(
            name="knowledge_base"
        )

    @staticmethod
    def transform(request: schemas.AssignRequest) -> schemas.AssignTransformedDTO:

        result = dict()
        result["QA"] = request.QA

        if len(result["QA"]) >= 5:
            result["QA"] = result["QA"][-5:]

        result["rag_results"] = Preprocessor._get_rag_results(
            result["QA"],
            request.mission_name,
            request.submission_name,
            request.task_sequence,
        )

        result["top_k"] = Preprocessor.top_k
        result["character_type"] = request.character

        result = schemas.AssignTransformedDTO(**result)

        return result

    @staticmethod
    def _get_rag_results(
        query_text_list: List[str],
        mission_name: str,
        submission_name: str,
        task_sequence: str,
    ) -> List[str]:
        result_set = set()
        for query_text in query_text_list:
            result_set.update(
                Preprocessor._query_similar_docs(
                    query_text,
                    metadata_filter={
                        "mission_name": mission_name,
                        "submission_name": submission_name,
                        "task_sequence": task_sequence,
                    },
                    n_results=Preprocessor.top_k,
                )
            )

        return list(result_set)

    @staticmethod
    def _query_similar_docs(
        query_text: str,
        metadata_filter: Optional[Dict[str, Any]] = None,
        n_results: int = 3,
    ) -> List[Dict[str, Any]]:

        where_condition = None
        if metadata_filter:
            where_condition = {
                "$and": [{key: value} for key, value in metadata_filter.items()]
            }

        results = Preprocessor.collection.query(
            query_texts=[query_text],
            where=where_condition,
            n_results=n_results,
            include=["documents"],
        )

        formatted_results = []
        for doc in results["documents"][0]:
            formatted_results.append(doc)

        if len(formatted_results) == 0:
            raise HTTPException(
                status_code=422,
                detail="Invalid Task Info (mission_name, submission_name, task_sequence)",
            )

        return formatted_results

    @staticmethod
    def _get_candidates(
        db_path: str, mission_name: str, submission_name: str, task_sequence: str
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
