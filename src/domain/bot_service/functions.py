from aiogram import Bot, Dispatcher
from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
import aiohttp

from src.configs.config import settings
from src.configs.logger_setup import logger
from src.domain.bot_service.models import FSMAdmin
from src.domain.vk_router_service.functions import VkRouterFunctions


class BotFunctions(VkRouterFunctions):

	def __init__(self, bot: Bot, dp: Dispatcher) -> None:
		super().__init__(bot)
		self.bot = bot
		self.dp = dp


	async def is_bot_in_group(self, message: Message, group_id: int, state: FSMContext) -> None:
		try:
			logger.info("Бот добавлен в группу")
			chat = await self.bot.get_chat(-group_id)

			bot_info = await self.bot.get_chat_member(chat_id=-group_id, user_id=self.bot.id)

			if bot_info.status in ChatMemberStatus.ADMINISTRATOR:
				await message.answer(
					f"Бот добавлен в группу: {chat.title} и является администратором в этой группе.")

				await state.update_data(telegram_group_id=message.text)
				await state.set_state(FSMAdmin.vk_group_id)

				await message.answer("Теперь отправьте Url группы Vk")

			else:
				await message.answer(
					f"Бот добавлен в группу: {chat.title} но НЕ является администратором в этой группе.")
				await message.answer("Сделайте Бота администратором группы и отправьте ID группы ещё раз")

		except TelegramBadRequest as e:
			logger.error(f"{e}")
			await message.answer("Некорректный ID группы. Пожалуйста, проверьте и попробуйте снова.")

		except Exception as e:
			logger.error(f"Произошла ошибка: {str(e)}")


	@staticmethod
	async def is_integer_string(value: str) -> int | bool:
		try:
			return int(value)

		except ValueError:
			return False


	@staticmethod
	async def check_vk_group(group_name: str) -> dict | bool:
		params = {
			'group_id': group_name,
			'access_token': settings.VK_APP_SERVICE_KEY,
			'v': settings.VK_API_VERSION
		}

		try:
			async with aiohttp.ClientSession() as session:
				async with session.get(settings.BASE_URL + "groups.getById", params=params, ssl=False) as response:
					data = await response.json()

			if "response" in data:
				for group in data["response"]["groups"]:
					logger.info(f"Имя группы: {group['name']}")
					return group

			elif "error" in data:
				logger.warn(f"Ошибка: {data['error']['error_msg']}")
				return False

		except Exception as e:
			logger.error(f"Ошибка: {e}")



