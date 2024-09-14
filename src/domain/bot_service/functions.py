from aiogram import Bot, Dispatcher
import aiohttp

from src.configs.config import settings
from src.configs.logger_setup import logger
from src.domain.vk_router_service.functions import VkRouterFunctions


class BotFunctions(VkRouterFunctions):

	def __init__(self, bot: Bot, dp: Dispatcher) -> None:
		super().__init__(bot)
		self.bot = bot
		self.dp = dp


	@staticmethod
	async def is_integer_string(value: str) -> int | bool:
		try:
			return int(value)

		except ValueError:
			return False


	@staticmethod
	async def check_vk_group(group_id: int) -> str | bool:
		params = {
			'group_id': group_id,
			'access_token': settings.VK_APP_SERVICE_KEY,
			'v': settings.VK_API_VERSION
		}

		try:
			async with aiohttp.ClientSession() as session:
				async with session.get(settings.BASE_URL + "groups.getById", params=params, ssl=False) as response:
					data = await response.json()

			if "response" in data:
				for group in data["response"]["groups"]:

					if group["type"] == "group":
						logger.info(f"Имя группы: {group['name']}")
						return group["name"]

			elif "error" in data:
				logger.warn(f"Ошибка: {data['error']['error_msg']}")
				return False

		except Exception as e:
			logger.error(f"Ошибка: {e}")



