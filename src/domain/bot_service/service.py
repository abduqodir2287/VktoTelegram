from aiogram.enums import ParseMode, ChatMemberStatus
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from src.configs.logger_setup import logger
from src.domain.bot_service.functions import BotFunctions
from src.domain.buttons import check_group, start_sending_keyboard, channel_or_group
from src.domain.bot_service.models import FSMAdmin
from src.domain.buttons import choice_group
from src.domain.vk_router_service.service import VkRouterService


class BotService(BotFunctions, VkRouterService):

	def __init__(self, bot: Bot, dp: Dispatcher) -> None:
		BotFunctions.__init__(self, bot, dp)
		VkRouterService.__init__(self, bot)
		self.bot = bot
		self.dp = dp


	@staticmethod
	async def start_bot_service(message: Message, state: FSMContext) -> None:
		logger.info("Бот стартанул!")
		current_state = await state.get_state()

		if current_state is not None:
			await state.clear()

		await message.answer(
			f"Привет {message.from_user.first_name}.\n"
			f"Сперва добавьте Бот на вашу группу или канал и сделайте его администратором",
			reply_markup=check_group,
			parse_mode=ParseMode.MARKDOWN
		)


	@staticmethod
	async def channel_or_group_service(message: Message) -> None:
		await message.answer(
			"Отлично! 🎉\n\n"
			"Пожалуйста, укажи, куда ты добавил этого бота:\n"
			"📢 На `Канал` или 🗣️ в `Группу`?",
			reply_markup=channel_or_group
		)

		logger.info("Сообщение о выборе между каналом и группой отправлено")


	@staticmethod
	async def get_id_in_group(message: Message) -> None:
		await message.answer(f"ID этой группы: {abs(message.chat.id)}")

		logger.info("ID группы успешно передано")


	@staticmethod
	async def get_channel_message(message: Message, state: FSMContext) -> None:
		await message.answer(
			"Хорошо. Перешлите мне любое сообщения из канала\n"
			"Которому добавили этот бот",
			reply_markup=ReplyKeyboardRemove()
		)

		await state.set_state(FSMAdmin.telegram_channel_id)

		logger.info("Пользователь добавил бота на канал!")


	@staticmethod
	async def get_channel_id_service(message: Message, state: FSMContext) -> None:
		if message.forward_from_chat:
			forward_chat_id = message.forward_from_chat.id
			forward_chat_title = message.forward_from_chat.title

			try:
				bot_member = await message.bot.get_chat_member(chat_id=forward_chat_id, user_id=message.bot.id)

				if bot_member:
					await message.answer(f"Бот добавлен в этот канал. Имя канала {forward_chat_title}")

					await state.update_data(telegram_group_id=abs(forward_chat_id))
					await state.set_state(FSMAdmin.vk_group_id)

					await message.answer("Теперь отправьте Url группы Vk")

			except TelegramBadRequest:
				await message.answer("Бот не добавлен в этот канал. \n"
				                     "Отправьте сообщения иэ канала, который добавлен этот бот")

		else:
			await message.answer("Сообщение не переслано из Канала")


	@staticmethod
	async def get_group_id(message: Message, state: FSMContext) -> None:
		await state.set_state(FSMAdmin.telegram_group_id)

		await message.answer(
			"Хорошо. Отправьте ID Группы который добавили этот бот\n\n"
			"Чтобы узнать ID вашей группы, отправьте `/get_id` на вашу группу.",
			parse_mode=ParseMode.MARKDOWN, reply_markup=ReplyKeyboardRemove()
		)


	async def check_group(self, message: Message, state: FSMContext) -> None:
		group_id = await self.is_integer_string(message.text)

		if group_id:
			await self.is_bot_in_group(message, group_id, state)

		else:
			logger.info("Некорректный ID Группы")
			await message.answer("Отправьте корректный ID Группы.\n"
			                     "Только цифры!")



	async def get_vk_group_id_service(self, message: Message, state: FSMContext) -> None:
		if message.text.startswith("https://vk.com/"):
			group_url = message.text
			group_name = group_url.strip('/').split('/')[-1]

			group_info = await self.check_vk_group(group_name)

			if group_info:
				await message.answer(
					f"Корректный Url Группы.\n"
					f"Имя группы {group_info['name'] if group_info['name'] is not None else group_info['screen_name']}."
				)

				await message.answer("Это ваша группа?\n"
				                     "Если нет то нажмите на кнопку 'Другое'", reply_markup=choice_group)

				group_wall = await self.get_wall(group_info["id"])
				wall = group_wall["response"]["items"]

				for event in wall:
					last_wall_post_id = event["id"]

					await state.update_data(
						vk_group_id=group_info["id"], last_post_id=last_wall_post_id, send_status=False)

				await state.set_state(FSMAdmin.yes_or_no)

			else:
				await message.answer("Некорректный Url группы. Пожалуйста, проверьте и попробуйте снова.")
		else:
			await message.answer("Некорректный Url группы. Url группы должно начинаться с `https://vk.com/`")


	@staticmethod
	async def group_choice_service(message: Message, state: FSMContext) -> None:
		if message.text == "Другое":
			logger.info("Другая группа!")

			await message.answer("Введите Url группы заново:", reply_markup=ReplyKeyboardRemove())
			await state.set_state(FSMAdmin.vk_group_id)

		elif message.text == "Да":
			logger.info("Правильный группа!")

			await message.answer(
				"Вы верно передали все параметры теперь можете начать отправления сообщений",
				reply_markup=start_sending_keyboard
			)

			await state.set_state(FSMAdmin.start_sending)


