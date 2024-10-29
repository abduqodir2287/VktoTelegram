import asyncio

import aiohttp
from aiogram.fsm.context import FSMContext

from src.configs.config import settings
from src.configs.logger_setup import logger
from src.domain.rabbitmq_service.functions import RabbitMQFunctions


class RabbitMQService(RabbitMQFunctions):

	def __init__(self) -> None:
		super().__init__()


	@staticmethod
	async def get_wall(group_id: int) -> dict:
		url = settings.BASE_URL + "wall.get"
		params = {
			"access_token": settings.VK_APP_SERVICE_KEY,
			"owner_id": -group_id,
			"v": settings.VK_API_VERSION,
			"count": 1
		}

		async with aiohttp.ClientSession() as session:
			async with session.get(url, params=params, ssl=False) as response:
				server_data = await response.json()

		return server_data


	async def get_wall_for_rabbit_mq(self, state: FSMContext) -> None:
		while True:
			group_data = await state.get_data()

			send_status = group_data["send_status"]
			vk_group_id = group_data["vk_group_id"]
			last_post_id = group_data["last_post_id"]

			if not send_status:
				break

			events = await self.get_wall(vk_group_id)

			for event in events["response"]["items"]:
				if event["id"] > last_post_id:
					logger.info(f"Есть новый события: {event['id']}")

					ready_to_add = await self.dict_formatter(vk_group_id, event)

					await self.add_event(ready_to_add)

			await asyncio.sleep(3)


