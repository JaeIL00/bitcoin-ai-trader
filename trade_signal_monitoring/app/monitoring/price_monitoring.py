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
               "tp": int 현재가
            }
            """
            print(data)


def get_trade_ws():
    asyncio.run(ws())


if __name__ == "__main__":
    get_trade_ws()
