from nadeulAI_SSE.src.confidential.constants import (
    AI_SERVER_BASE_URL,
    AI_SERVER_COUNT,
    REDIS_HOST,
    REDIS_PORT,
)
from httpx import TimeoutException, AsyncClient
import asyncio
import logging
import redis.asyncio as aioredis


class Awaker:
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)
    r_lb = aioredis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
    period = 3000

    @staticmethod
    async def awaker_on():
        print("awaker: on")
        # while True:
        #     for machine_idx in range(AI_SERVER_COUNT):
        #         await Awaker.r_lb.set(f"ai_server_is_busy_{machine_idx}", 1, ex=40)
        #         await Awaker.keep_ai_server_awake(machine_idx)
        #         await Awaker.r_lb.delete(f"ai_server_is_busy_{machine_idx}")
        #         await asyncio.sleep(Awaker.period)

    @staticmethod
    async def keep_ai_server_awake(ai_server_idx):
        try:
            Awaker.logger.info(f"awake: {ai_server_idx}")
            candidates = [
                "화성행궁은 조선 시대의 임시 왕궁으로, 수원 화성에 위치해 있습니다",
                " 행궁(行宮)은 왕이 지방에 머물거나 잠시 머무를 때 사용하는 임시 궁궐을 의미하는데, 화성행궁은 그중에서도 가장 크고 중요한 행궁 중 하나입니다",
                " 조선 정조(正祖) 시기에 건립된 이 궁궐은 수원 화성의 중심부에 위치하며, 왕실의 정치적, 군사적 중심지로서 다양한 역할을 했습니다",
                " 건립 배경\n화성행궁은 조선 제22대 왕인 정조가 1794년부터 1796년까지 수원에 축조한 수원 화성의 일부로 건설되었습니다",
                " 정조는 그의 아버지 사도세자(장헌세자)의 무덤인 **현륭원(지금의 융릉)**을 수원으로 옮기고 이를 참배하기 위한 목적으로 화성행궁을 건립했습니다",
                " 정조는 아버지에 대한 효심과 왕권 강화를 위해 자주 화성에 머물렀고, 따라서 임시 거처로서 화성행궁이 중요한 역할을 했습니다",
                " 역할 및 기능\n화성행궁은 단순한 임시 거처가 아니라 여러 가지 기능을 수행했습니다",
                "\n\n임시 궁궐: 정조는 화성에 머물며 정치를 논하고, 국정 전반을 관리했습니다",
                " 따라서 화성행궁은 왕이 머물 수 있는 숙소뿐만 아니라 신하들과 정무를 논의하는 장소로도 사용되었습니다",
                "\n군사적 중심지: 수원 화성은 그 자체로 군사적 요새였으며, 화성행궁은 그 중심에 위치한 지휘소 역할을 했습니다",
                " 정조는 화성에서 군사 훈련을 자주 실시했고, 이를 통해 왕권 강화를 도모했습니다",
                "\n문화 및 의례의 공간: 정조는 화성행궁에서 여러 의례와 연회를 열었으며, 특히 그의 어머니 혜경궁 홍씨의 회갑잔치를 성대하게 열었습니다",
                " 이 행사는 조선의 정치와 문화를 동시에 상징하는 중요한 행사였습니다",
                " 건축 구조\n화성행궁은 당시 가장 큰 규모의 행궁으로, 약 600여 칸에 달하는 방들이 있었습니다",
                " 현재 복원된 건물들도 여전히 그 규모와 아름다움을 자랑하며, 주요 건물로는 다음과 같은 것이 있습니다",
                "\n\n봉수당: 정조가 어머니 혜경궁 홍씨의 회갑연을 열었던 장소로, 행궁에서 가장 화려하고 상징적인 건물입니다",
                "\n낙남헌: 정조가 신하들과 정무를 논하고 직접 군사 훈련을 지휘하던 공간입니다",
                "\n장락당: 정조가 화성에 머무를 때 실제로 거주했던 생활 공간입니다",
                " 정조는 여기서 어머니와 함께 시간을 보냈습니다",
                "\n득중정: 이곳은 정조가 활쏘기 훈련을 하던 곳으로, 군사 훈련의 중요한 부분을 차지했습니다",
                " 화성행궁의 역사적 의의\n정조의 개혁 정치와 왕권 강화: 정조는 수원 화성을 통해 왕권 강화를 위한 자신의 정치적 이상을 실현하려 했습니다",
                " 화성행궁은 정조의 효심과 정치적 이상을 결합한 상징적 장소로, 특히 개혁적 정치와 군사적 훈련의 중심지였습니다",
                "\n문화유산: 정조 사후에도 화성행궁은 조선의 중요한 문화유산으로 남았습니다",
                " 그러나 한국전쟁과 일제강점기를 거치면서 많은 부분이 파괴되었고, 현재는 복원 작업이 진행되어 많은 부분이 복구된 상태입니다",
                " 현재의 화성행궁\n현재 화성행궁은 유네스코 세계문화유산에 등재된 수원 화성의 일부로, 많은 관광객이 찾는 명소입니다",
                " 복원된 행궁에서는 다양한 문화행사와 역사 체험 프로그램이 운영되며, 조선 시대의 궁궐 문화를 체험할 수 있는 기회를 제공합니다",
                "\n\n관람: 방문객들은 정조 시대의 화려한 궁중 문화를 재현한 행사, 전통 공연, 궁궐 복장 체험 등을 할 수 있습니다",
                "\n문화재: 화성행궁은 한국의 국보급 문화재로서, 조선 후기 건축물과 궁궐 문화를 연구하는 중요한 자료입니다",
                " 정조의 행차 재현 행사\n매년 화성행궁에서는 정조대왕 능행차라는 이름으로 정조의 행차를 재현하는 대규모 퍼레이드가 열립니다",
                " 이 행사는 정조가 아버지 사도세자의 능을 참배하러 가는 여정을 재현한 것으로, 역사적 의미를 되새기고 당시의 문화를 체험할 수 있는 특별한 행사입니다",
                "\n\n화성행궁은 조선 왕조의 정치, 군사, 문화의 중심지로서 큰 역할을 했고, 오늘날에는 그 역사적 가치를 기리며 다양한 문화 체험의 장이 되고 있습니다",
            ]
            async with AsyncClient(
                base_url=AI_SERVER_BASE_URL.format(ai_server_idx)
            ) as async_client:
                async with async_client.stream(
                    "POST",
                    "/",
                    json={
                        "character_type": 2,
                        "QA": ["화성행궁에 대해 알려줘."],
                        "candidates": candidates,
                        "top_k": 3,
                    },
                    timeout=100,
                ) as response:
                    result_text = ""
                    is_first = True
                    start_signal = {
                        "type": "signal",
                        "contents": "start",
                        "verbose": "내 차례가 되어 AI 모델과 스트리밍 세션이 연결됨, 로딩 뷰 종료",
                    }

                    async for chunk in response.aiter_text():
                        if is_first:
                            is_first = False
                        result_text += chunk
                        model_output = {
                            "type": "model_output",
                            "contents": result_text,
                            "verbose": "질문에 대한 모델 출력입니다.",
                        }
                    if is_first:
                        pass
        except TimeoutException:
            Awaker.logger.error(f"Timeout occurred for server {ai_server_idx}")
        except Exception as e:
            Awaker.logger.error(
                f"An error occurred for server {ai_server_idx}: {str(e)}"
            )


if __name__ == "__main__":
    asyncio.run(Awaker.awaker_on())
