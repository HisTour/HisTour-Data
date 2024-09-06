import pytest
import time
from src.requests.rag import retrieve
from test.test_data import qa_inputs

# Fixtures


# Function Unit Test

@pytest.mark.rag_functest
@pytest.mark.parametrize("qa_input", qa_inputs)
def test_retrieve(qa_input):
    start_time = time.time()
    output = retrieve(QA=qa_input, task_id=0)
    elapsed_time = time.time() - start_time
    print(f"output : {output}")
    print(f"elapsed_time : {elapsed_time}")