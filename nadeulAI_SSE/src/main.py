from fastapi import FastAPI

app = FastAPI(docs_url="/docs", openapi_url="/open-api-docs")

ai_server_num = 6

ai_servers = [{"id": i, "url":f""}]
