import pytest
import redis
from httpx import AsyncClient
from src.main import app
from test.test_utils import is_valid_url


# Fixtures


# API Unit Test

@pytest.mark.urlrouter_unittest
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "qa_input",  # 파라미터 이름 정의
    [
        (["창룡문이 뭐야?"]),  # 테스트 케이스 1
    ]
)
async def test_urlrouter():
    async with AsyncClient(app=app, base_url="http://0.0.0.0:8000") as async_client:
        url_router_response = await async_client.post(
            "/urlrouter",
            json={
                "task_id": 0,
                "QA": qa_input,
                "type": "test"
            }
        )
        assert url_router_response.status_code == 200
        assert url_router_response.json().get("url") is not None
        assert is_valid_url(url_router_response.json()["url"])