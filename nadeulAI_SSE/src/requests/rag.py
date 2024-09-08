from typing import List, Dict
from fastapi import HTTPException
from httpx import AsyncClient
import sqlite3
import yaml

with open("credential.yaml") as f:
    credentials = yaml.safe_load(f)
    EMBEDDING_BASE_URL = credentials["embedding_base_url"]

TOP_K = 3


def qa_2_str_chat_format(QA: List[str]) -> str:
    str_chat_format = ""
    for idx, item in enumerate(QA):
        if idx % 2 == 0: # Q
            message = f"Q: {item}\n"
        else: # A
            message = f"A: {item}\n"
        str_chat_format.append(message)
    
    return str_chat_format

async def request_to_embedding_server(str_chat_format:str, 
                                      candidate_sentences: List[str],
                                      top_k: int) -> List[str]:
    async with AsyncClient(base_url=EMBEDDING_BASE_URL) as async_client:
        embedding_response = await async_client.get(
            "/",
            json={
                "prompt": str_chat_format,
                "candidates": candidate_sentences,
                "top_k": top_k
            }
        )

        if embedding_response.status_code != 200:
            try:
                error_detail = embedding_response.json()  # JSON 응답에서 에러 메시지 추출
                raise HTTPException(status_code=embedding_response.status_code,
                                    detail=error_detail)
            except ValueError:  # 응답이 JSON 형식이 아닌 경우
                raise HTTPException(status_code=embedding_response.status_code,
                                    detail="Unknown error occurred")
            
        else:
            return embedding_response.json()["rag_result"]
    

async def retrieve(QA: List[str], task_id: int):
    # Preprocess
    if len(QA) == 0 or len(QA) % 2 == 0:
        raise HTTPException(status_code=400, detail="QA list의 원소의 개수는 0개이거나 짝수개이면 안됩니다.")
    
    # Make Query Sentence 
    str_chat_format = qa_2_str_chat_format(QA)

    # Connect Local DB and Get Candidate Sentences
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM task_document WHERE task_id=?", (task_id,))
    rows = cursor.fetchall()

    candidate_sentences = []
    for row in rows:
        document = row["document"]
        candidate_sentences += document.split(".").rstrip()

    rag_result = await request_to_embedding_server(str_chat_format=str_chat_format,
                                                   candidate_sentences=candidate_sentences,
                                                   top_k=TOP_K)
    return rag_result


        



    
    
    