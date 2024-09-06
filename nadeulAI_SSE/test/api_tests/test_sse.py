import pytest
from httpx import AsyncClient
from src.main import app
from test.test_utils import is_valid_sse_response


# Fixtures


# API Unit Test

@pytest.mark.sse_apitest
@pytest.mark.asyncio
async def test_sse():
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        async with async_client.stream("GET", "/sse/0") as sse_response:
            assert sse_response.status_code == 200  # 응답 코드가 200이어야 함
            async for line in sse_response.aiter_lines():
                if line:  # 빈 줄은 무시
                    print(f"Received Response: {line}")
                    assert is_valid_sse_response(line)
                    
                    