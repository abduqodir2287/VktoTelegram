import aio_pika
import json
from pika.exceptions import ChannelClosed

from src.configs.config import settings
from src.configs.logger_setup import logger


class RabbitMQFunctions:

	def __init__(self) -> None:
		self.connection = None
		self.channel = None
		self.queue = None


	async def connect_to_rabbitmq(self):
		self.connection = await aio_pika.connect_robust(
			host=settings.RMQ_HOST,
			port=settings.RMQ_PORT,
			login=settings.RMQ_USER,
			password=settings.RMQ_PASSWORD,
			heartbeat=60
		)
		logger.info("Connection created!")

		self.channel = await self.connection.channel()
		logger.info("Channel created!")

		self.queue = await self.channel.declare_queue(settings.RMQ_ROUTING_KEY, durable=True)


	@staticmethod
	async def dict_formatter(vk_group_id: int, event: dict) -> str:
		ready_dict = {
			"vk_group_id": vk_group_id,
			"event": event
		}

		return json.dumps(ready_dict)


	async def add_event(self, body: str) -> None:
		if self.channel is None or self.connection is None:
			await self.connect_to_rabbitmq()

		await self.channel.default_exchange.publish(
			aio_pika.Message(body=body.encode()),
			routing_key=settings.RMQ_ROUTING_KEY
		)

		logger.info("Event added to Rabbit MQ!")


	async def get_message(self, vk_group_id: int) -> list[dict] | None:
		try:
			messages = []

			if self.channel is None or self.connection is None:
				await self.connect_to_rabbitmq()

			while True:
				try:
					message = await self.queue.get(no_ack=False)

				except aio_pika.exceptions.QueueEmpty:
					break

				if message:
					body = json.loads(message.body.decode())

					if body.get("vk_group_id") == vk_group_id:
						messages.append(body)
						await message.ack()

				else:
					break

			return messages

		except ChannelClosed:
			logger.warning("Channel closed by broker. No messages available yet.")
			return None


	async def rmq_close(self) -> None:
		if self.channel:
			await self.channel.close()

		if self.connection:
			await self.connection.close()

		logger.info("RabbitMQ connection closed.")

