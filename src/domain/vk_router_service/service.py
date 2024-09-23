from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
import asyncio

from src.configs.logger_setup import logger
from src.domain.bot_service.models import FSMAdmin
from src.domain.vk_router_service.functions import VkRouterFunctions
from src.domain.buttons import start_sending_keyboard, stop_sending_keyboard


class VkRouterService(VkRouterFunctions):

	def __init__(self, bot: Bot) -> None:
		super().__init__(bot)
		self.bot = bot


	async def start_send_messages(self, message: Message, state: FSMContext) -> None:
		logger.info("Начался отправка сообщений!")

		await message.reply("Начинаю отправку сообщений!", reply_markup=stop_sending_keyboard)

		await state.set_state(FSMAdmin.stop_sending)
		await state.update_data(send_status=True)

		await self.send_message(state)


	async def send_message(self, state: FSMContext) -> None:
		while True:
			group_data = await state.get_data()

			chat_id = group_data["telegram_group_id"]
			send_status = group_data["send_status"]
			vk_group_id = group_data["vk_group_id"]
			last_post_id = group_data["last_post_id"]

			if not send_status:
				break

			events = await self.get_wall(vk_group_id)

			for event in events["response"]["items"]:
				if event["id"] > last_post_id:
					logger.info(f"Есть новый события: {event['id']}")

					await self.check_event(event, int(chat_id))

					await state.update_data(last_post_id=event["id"])

			await asyncio.sleep(3)


	@staticmethod
	async def stop_sending_messages(message: Message, state: FSMContext) -> None:
		await state.update_data(send_status=False)
		logger.info("Stop sending messages")
		await message.answer("Отправка сообщений приостановлена!", reply_markup=start_sending_keyboard)

		await state.set_state(FSMAdmin.start_sending)


