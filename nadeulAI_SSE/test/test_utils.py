import re
import json

def is_valid_url(url: str):
    ipv4_url_pattern = re.compile(
        r'^(https?)://'  # http 또는 https 프로토콜
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'  # IPv4 주소
        r'(?::\d+)?'  # 선택적인 포트 번호
        r'(?:/?|[/?]\S+)?$', re.IGNORECASE)  # 선택적인 경로 및 쿼리

    return re.match(ipv4_url_pattern, url) is not None

def is_valid_sse_response(message: str):
    if "data:" not in message:
        return False
    
    event_data = message.replace("data: ", "")
    event_dict = json.loads(event_data)

    if event_dict["type"] not in ["signal", "model_output"]:
        return False
    if event_dict.get("contents") is None:
        return False
    if event_dict.get("verbose") is None:
        return False
    
    return True
    
