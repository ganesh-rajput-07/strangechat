import time
from app.services.redis_client import redis_client
from app.websocket.manager import manager


class Matchmaker:
    def __init__(self):
        self.redis = redis_client
        self.reconnect_timeout = 20  # seconds to wait before finding new partner

    async def try_match(self, user_id: str) -> bool:
        """
        Try to find a match for user.
        First tries to reconnect with previous partner, then checks queue.
        Returns True if matched, False if added to queue
        """
        # First, try to reconnect with previous partner
        previous_partner, timestamp = self.redis.get_previous_partner(user_id)
        if previous_partner:
            # Check if previous partner is still in queue (waiting to reconnect)
            if self.redis.is_user_in_queue(previous_partner):
                # Check if within timeout window
                current_time = int(time.time())
                if current_time - timestamp <= self.reconnect_timeout:
                    # Remove from queue and reconnect
                    self.redis.remove_user_from_queue(previous_partner)
                    self.redis.remove_previous_partner(user_id)
                    self.redis.remove_previous_partner(previous_partner)
                    
                    # Pair the users
                    self.redis.set_active_chat(user_id, previous_partner)
                    manager.pair_users(user_id, previous_partner)
                    
                    # Notify both users
                    await manager.send_personal_message({
                        "type": "system",
                        "message": "Stranger connected"
                    }, user_id)
                    await manager.send_personal_message({
                        "type": "system",
                        "message": "Stranger connected"
                    }, previous_partner)
                    
                    return True

        # Check if there's someone waiting in queue
        queue_length = self.redis.get_queue_length()
        
        if queue_length >= 1:
            # Get partner from queue
            partner_id = self.redis.get_from_queue()
            if partner_id and partner_id != user_id:
                # Remove previous partner record if exists
                self.redis.remove_previous_partner(user_id)
                
                # Pair the users
                self.redis.set_active_chat(user_id, partner_id)
                manager.pair_users(user_id, partner_id)
                
                # Notify both users
                await manager.send_personal_message({
                    "type": "system",
                    "message": "Stranger connected"
                }, user_id)
                await manager.send_personal_message({
                    "type": "system",
                    "message": "Stranger connected"
                }, partner_id)
                
                return True
        
        # No match found, add to queue
        self.redis.add_to_queue(user_id)
        return False

    async def handle_next(self, user_id: str):
        """
        Handle 'next' button click
        Remove current chat and requeue both users
        """
        partner_id = manager.get_partner(user_id)
        
        if partner_id:
            # Store previous partners for potential reconnection
            self.redis.set_previous_partner(user_id, partner_id, self.reconnect_timeout)
            self.redis.set_previous_partner(partner_id, user_id, self.reconnect_timeout)
            
            # Remove from active chats
            self.redis.remove_active_chat(user_id)
            manager.disconnect(user_id)
            manager.disconnect(partner_id)
            
            # Notify partner
            await manager.send_personal_message({
                "type": "system",
                "message": "Stranger left"
            }, partner_id)
            
            # Requeue both users
            await self.try_match(user_id)
            await self.try_match(partner_id)


# Global matchmaker instance
matchmaker = Matchmaker()
