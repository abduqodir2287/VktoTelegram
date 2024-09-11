from redis import Redis

from src.configs.config import settings

class RedisClient:

	def __init__(self) -> None:
		self.redis_client = Redis(
			host=settings.REDIS_HOST, port=settings.REDIS_PORT,
			db=settings.REDIS_DATABASE, decode_responses="utf-8"
		)


	def set(self, name: str | int, data: str) -> None:
		self.redis_client.set(name, data)


	def get(self, name: str | int) -> str:
		if self.redis_client.exists(name):
			return self.redis_client.get(name)


