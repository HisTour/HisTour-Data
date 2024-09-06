import pytest
import time
from src.langchain.rag import retrieve


# Fixtures


# Function Unit Test

@pytest.mark.rag_functest
@pytest.mark.parametrize(
    "qa_input",  # 파라미터 이름 정의
    [
        (["창룡문이 뭐야?"]),  # 테스트 케이스 1
    ]
)
def test_retrieve():
    start_time = time.time()
    output = retrieve(QA=qa_input, task_id=0)
    elapsed_time = time.time() - start_time
    print(f"output : {output}")
    print(f"elapsed_time : {elapsed_time}")