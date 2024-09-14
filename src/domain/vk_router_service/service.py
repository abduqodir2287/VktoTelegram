from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
import aiohttp
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

		await message.reply("Начинаю отправку сообщений!", reply_markup=stop_sending_keyboard)

		await state.set_state(FSMAdmin.stop_sending)
		await state.update_data(send_status=True)

		await self.send_message(state)


	async def send_message(self, state: FSMContext) -> None:
		while True:
			group_data = await state.get_data()

			chat_id = group_data["telegram_group_id"]
			send_status = group_data["send_status"]

			if not send_status:
				break

			long_poll_server_data = await self.get_server_key(group_data["vk_group_id"], group_data["vk_group_token"])

			logger.info("Check events")

			long_poll_url = (f"{long_poll_server_data['response']['server']}"
			                 f"?act=a_check&key={long_poll_server_data['response']['key']}&"
			                 f"ts={int(group_data['ts'])}&wait=2")

			async with aiohttp.ClientSession() as session:
				async with session.get(long_poll_url, ssl=False) as response:
					events = await response.json()
					logger.info(f"events: {events}")

			await state.update_data(ts=events['ts'])

			if events['updates']:
				for event in events['updates']:
					await self.check_event(event, int(chat_id))

			await asyncio.sleep(4)


	@staticmethod
	async def stop_sending_messages(message: Message, state: FSMContext) -> None:
		await state.update_data(send_status=False)
		logger.info("Stop sending messages")
		await message.answer("Отправка сообщений приостановлена!", reply_markup=start_sending_keyboard)

		await state.set_state(FSMAdmin.start_sending)




