import pytest
import time
from nadeulAI_SSE.src.requests.rag import retrieve
from nadeulAI_SSE.test.test_data import qa_inputs

# Fixtures


# Function Unit Test

# @pytest.mark.rag_functest
@pytest.mark.parametrize("qa_input", qa_inputs)
@pytest.mark.asyncio
async def test_retrieve(qa_input):
    start_time = time.time()
    output = await retrieve(QA=qa_input, task_id=0)
    elapsed_time = time.time() - start_time
    print(f"output : {output}")
    print(f"elapsed_time : {elapsed_time}")