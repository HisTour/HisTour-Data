import sqlite3
from pprint import pprint
import chromadb
from chromadb.utils import embedding_functions
from FlagEmbedding import BGEM3FlagModel

conn = sqlite3.connect("python_inner.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM knowledges")
rows = cursor.fetchall()
print("COMPLETE: SQLite Fetch")

# BGEM3FlagModel 초기화
embedding_model_name = "BAAI/bge-m3"
embedding_model = BGEM3FlagModel(embedding_model_name, use_fp16=True)
print("COMPLETE: BGEM3FlagModel Import")


# 커스텀 임베딩 함수 정의
def custom_embedding_function(texts):
    # BGEM3FlagModel을 사용하여 텍스트 임베딩 생성
    embeddings = embedding_model.encode(texts, batch_size=12, max_length=512)[
        "dense_vecs"
    ]
    return embeddings.tolist()


# Chroma 클라이언트 초기화
client = chromadb.PersistentClient(path="vector_db")
print("COMPLETE: Chroma Client")

# 기본 임베딩 모델을 사용하여 컬렉션 생성
collection = client.get_or_create_collection(
    name="knowledge_base", metadata={"hnsw:space": "cosine"}
)
print("COMPLETE: Chroma Collection")

for row in rows[1:]:
    mission_name = row[1]
    submission_name = row[2]
    task_sequence = row[3]
    knowledge = list(row[4].split(".")[:-1])
    knowledge = [s.strip() for s in knowledge if len(s) > 5]

    # 메타데이터 설정
    metadata = {
        "mission_name": mission_name,
        "submission_name": submission_name,
        "task_sequence": task_sequence,
    }

    # 각 지식 청크를 벡터 DB에 추가
    for i, chunk in enumerate(knowledge):
        collection.add(
            documents=[chunk],
            metadatas=[metadata],
            ids=[f"{mission_name}_{submission_name}_{i}"],
        )
    print(f"COMPLETE: {mission_name}_{submission_name}_{i}")

# 벡터 DB를 파일로 저장
conn.close()
