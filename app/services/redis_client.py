import redis
import os
import time


class RedisClient:
    def __init__(self):
        self.redis_client = None

        self.redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            password=os.getenv("REDIS_PASSWORD"),  # 🔥 important
            db=int(os.getenv("REDIS_DB", 0)),      # default is fine
            decode_responses=True,
            ssl=True  # 🔥 Leapcell usually requires SSL
        )
        # Test connection 
            try:
                self.redis_client.ping()
                print("✅ Redis connected successfully")
            except Exception as e:
                print("❌ Redis connection failed:", e)

    def add_to_queue(self, user_id: str):
        """Add user to waiting queue"""
        self.redis_client.lpush("waiting_queue", user_id)

    def get_from_queue(self) -> str:
        """Get user from waiting queue (FIFO)"""
        return self.redis_client.rpop("waiting_queue")

    def get_queue_length(self) -> int:
        """Get number of users in queue"""
        return self.redis_client.llen("waiting_queue")

    def set_active_chat(self, user_a: str, user_b: str):
        """Store active chat pair"""
        self.redis_client.hset("active_chats", user_a, user_b)
        self.redis_client.hset("active_chats", user_b, user_a)

    def get_active_chat(self, user_id: str) -> str:
        """Get partner for user"""
        return self.redis_client.hget("active_chats", user_id)

    def remove_active_chat(self, user_id: str):
        """Remove user from active chats"""
        partner = self.redis_client.hget("active_chats", user_id)
        if partner:
            self.redis_client.hdel("active_chats", user_id)
            self.redis_client.hdel("active_chats", partner)

    def remove_user_from_queue(self, user_id: str):
        """Remove user from waiting queue"""
        self.redis_client.lrem("waiting_queue", 0, user_id)

    def set_previous_partner(self, user_id: str, partner_id: str, timeout: int = 20):
        """Store previous partner with timestamp for reconnection"""
        key = f"previous_partner:{user_id}"
        self.redis_client.hset(key, "partner_id", partner_id)
        self.redis_client.hset(key, "timestamp", str(int(time.time())))
        self.redis_client.expire(key, timeout)

    def get_previous_partner(self, user_id: str) -> tuple:
        """Get previous partner info (partner_id, timestamp) if exists and within timeout"""
        key = f"previous_partner:{user_id}"
        data = self.redis_client.hgetall(key)
        if data and "partner_id" in data and "timestamp" in data:
            return data["partner_id"], int(data["timestamp"])
        return None, None

    def remove_previous_partner(self, user_id: str):
        """Remove previous partner record"""
        key = f"previous_partner:{user_id}"
        self.redis_client.delete(key)

    def is_user_in_queue(self, user_id: str) -> bool:
        """Check if user is currently in waiting queue"""
        return self.redis_client.lpos("waiting_queue", user_id) is not None


# Global Redis client instance
redis_client = RedisClient()
