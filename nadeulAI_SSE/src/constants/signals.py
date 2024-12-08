from nadeulAI_SSE.src.schemas import Signal
from dataclasses import asdict

URL_CONNECTED_SIGNAL = Signal(
    type="signal",
    contents="url_connected",
    verbose="Spring 서버에서 받은 URL과 연결됨, SSE 연결 시작",
)

START_SIGNAL = Signal(
    type="signal",
    contents="start",
    verbose="내 차례가 되어 AI 모델과 스트리밍 세션이 연결됨, 로딩 뷰 종료",
)


STOP_SIGNAL = Signal(
    type="signal", contents="finish", verbose="스트리밍 세션 종료 및 SSE 종료"
)
