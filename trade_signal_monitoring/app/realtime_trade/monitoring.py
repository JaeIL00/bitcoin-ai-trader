import websockets
import asyncio
import json

url = "wss://api.upbit.com/websocket/v1"


async def ws():
    subscribe_fmt = [
        {"ticket": "trade-websocket"},
        {"type": "ticker", "codes": ["KRW-BTC"], "isOnlyRealtime": True},
        {"format": "SIMPLE"},
    ]
    subscribe_data = json.dumps(subscribe_fmt)

    async with websockets.connect(url) as websocket:

        await websocket.send(subscribe_data)
        while True:
            response = await websocket.recv()
            data = json.loads(response)
            """
            {
                'ty': 'trade', 
                'cd': 'KRW-BTC', 
                'tms': 1740572722056, 체결 시점 (utc(+0)임. 한국 현재시간 9시 25분)
                'td': '2025-02-26', 
                'ttm': '12:25:22', 
                'ttms': 1740572722031, 
                'tp': 128248000.0, 체결 가격
                'tv': 7.797e-05, 체결량
                'ab': 'BID', 매수/매도 구분 (ASK : 매도, BID : 매수)
                'pcp': 129715000.0, 전일 종가
                'c': 'FALL', 전일 대비 방향 
                'cp': 1467000.0, 전일 대비 변동폭
                'sid': 17405727220310000, 체결 번호
                'bap': 128248000, 최우선 매도 호가
                'bas': 0.05545175, 최우선 매도 잔량
                'bbp': 128213000, 최우선 매수 호가 
                'bbs': 0.00199913, 최우선 매수 잔량
                'st': 'REALTIME'
            }
                """
            print(data)


def get_trade_ws():
    asyncio.run(ws())
