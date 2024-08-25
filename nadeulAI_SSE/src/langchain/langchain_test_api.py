from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEndpoint
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableSequence
from dotenv import load_dotenv
import os
import sys

from histour_ai.src.constants import *

load_dotenv(dotenv_path=ENV_PATH)
os.environ["HUGGINGFACEHUB_API_TOKEN"] = os.getenv("HUGGINGFACEHUB_API_TOKEN")

repo_id = "MLP-KTLim/llama3-Bllossom"

# HuggingFaceEndpoint 객체 생성
llm = HuggingFaceEndpoint(
    repo_id=repo_id,
    max_new_tokens=256,
    temperature=0.2,
)

template = """<|system|>
You are a helpful assistant.<|end|>
<|user|>
{question}<|end|>
<|assistant|>"""

prompt = PromptTemplate.from_template(template)

chain = prompt | llm | StrOutputParser()

question = "한국의 수도는 어디지?"

for chunk in chain.stream({"question": question}):
    print(chunk, end="", flush=True)
    sys.stdout.flush()

print()
# response = chain.invoke({"question": question})

# print(response)
