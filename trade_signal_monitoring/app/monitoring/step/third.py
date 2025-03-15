import requests
from log_generator import set_logger
from api.api import get_vector_store_similar_ai

logger = set_logger()


def ai_rag_news():
    responses = []
    for _ in range(10):  # 10번 요청
        judge_response = get_vector_store_similar_ai()
        logger.info(f"judge_response: {judge_response}")
        # None 체크 후 응답 추가
        responses.append(process_response(judge_response["answer"]))

    # 응답 빈도 카운트
    counts = {"YES": 0, "NO": 0, "NEUTRAL": 0, "UNKNOWN": 0}
    for resp in responses:
        counts[resp] += 1

    # UNKNOWN 제외하고 최다 응답 찾기
    filtered_counts = {k: v for k, v in counts.items() if k != "UNKNOWN"}

    # 유효한 응답이 없는 경우
    if not filtered_counts:
        return "UNDECIDED", 0

    max_response = max(filtered_counts, key=filtered_counts.get)
    valid_responses = len(responses) - counts["UNKNOWN"]
    confidence = (
        filtered_counts[max_response] / valid_responses if valid_responses > 0 else 0
    )

    # 신뢰도가 특정 임계값을 넘을 때만 결정
    if confidence >= 0.6:
        return max_response, confidence
    else:
        return "UNDECIDED", confidence


def process_response(response):
    """AI 응답을 간단하게 처리"""
    if response is None:
        return "UNKNOWN"

    # 대소문자 무시, 공백 제거
    response = response.strip().upper()

    # 첫 단어만 추출
    first_word = response.split()[0] if response else ""

    # 간단한 분류
    if first_word == "YES":
        return "YES"
    elif first_word == "NO":
        return "NO"
    elif first_word == "NEUTRAL":
        return "NEUTRAL"
    else:
        return "UNKNOWN"
