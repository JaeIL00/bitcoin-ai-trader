import requests


def get_trade_ticks_api_call(days_ago=0):
    try:
        headers = {"accept": "application/json"}

        response = requests.get(
            f"https://api.upbit.com/v1/trades/ticks?market=KRW-BTC&count=500&days_ago={days_ago}",
            headers=headers,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise Exception(f"업비트 체결가 호출 중 오류 발생: {e}") from e


if __name__ == "__main__":
    result = {}
    for i in range(7):
        resfe = get_trade_ticks_api_call(i + 1)
        result[f"day_ago_{i+1}"] = resfe

    rfefe = analyze_volume_from_daily_ticks(result)
    print(rfefe)
