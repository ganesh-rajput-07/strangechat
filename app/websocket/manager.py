from typing import Dict, Optional
from fastapi import WebSocket
import uuid


class ConnectionManager:
    def __init__(self):
        # Store active connections: user_id -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}
        # Store chat pairs: user_id -> partner_id
        self.chat_pairs: Dict[str, str] = {}

    async def connect(self, websocket: WebSocket) -> str:
        """Accept connection and generate user_id"""
        await websocket.accept()
        user_id = str(uuid.uuid4())
        self.active_connections[user_id] = websocket
        return user_id

    def disconnect(self, user_id: str):
        """Remove user from active connections"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        # Remove from chat pairs
        if user_id in self.chat_pairs:
            partner_id = self.chat_pairs[user_id]
            del self.chat_pairs[user_id]
            if partner_id in self.chat_pairs:
                del self.chat_pairs[partner_id]

    def pair_users(self, user_a: str, user_b: str):
        """Pair two users for chat"""
        self.chat_pairs[user_a] = user_b
        self.chat_pairs[user_b] = user_a

    def get_partner(self, user_id: str) -> Optional[str]:
        """Get partner's user_id"""
        return self.chat_pairs.get(user_id)

    async def send_personal_message(self, message: dict, user_id: str):
        """Send message to specific user"""
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            await websocket.send_json(message)

    async def broadcast_to_pair(self, message: dict, user_id: str):
        """Send message to user's partner"""
        partner_id = self.get_partner(user_id)
        if partner_id:
            await self.send_personal_message(message, partner_id)


# Global manager instance
manager = ConnectionManager()
