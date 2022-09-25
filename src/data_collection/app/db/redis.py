from typing import Optional

import aioredis

from app import init_logger


log = init_logger(__name__)


class RedisManager:
    """Manage a Redis DB connection and CRUD operations

    Mainly used to keep the current number of messages (transaction hashes) in a given topic.
    """

    def __init__(self, redis_url: str, topic: str) -> None:
        """
        Args:
            redis_url (str): the url to a Redis database
            topic (str): the topic that this manager is associated with (topic=node name)
        """
        # The redis database instance
        self.redis = aioredis.from_url(redis_url, decode_responses=True)
        # The key used for storing the number of transactions in Redis
        self.key = f"{topic}_n_transactions"

    async def get_n_transactions(self) -> Optional[int]:
        """Return the number of unprocessed transactions."""
        if res := await self.redis.get(self.key):
            return int(res)
        return None

    async def incrby_n_transactions(self, incr_by: int = 1):
        """Increment the number of transactions by the given argument"""
        await self.redis.incrby(self.key, incr_by)

    async def decr_n_transactions(self):
        """Decrement the number of transactions by one"""
        await self.redis.decr(self.key)
