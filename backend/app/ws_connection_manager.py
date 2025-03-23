import json
from typing import Dict, List
from fastapi import WebSocket


class WsConnectionManager:
    def __init__(self):
        # 활성 WebSocket 연결 목록
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        # 새 WebSocket 연결 수락
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        # 연결 해제 처리
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict):
        # 타임스탬프 추가 (없는 경우)
        # 모든 활성 연결에 메시지 전송
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                print(f"메시지 전송 실패: {e}")
                # 실패한 연결은 끊어진 것으로 간주하고 목록에서 제거 가능
                # self.disconnect(connection)
