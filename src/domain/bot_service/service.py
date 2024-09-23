from aiogram.enums import ParseMode, ChatMemberStatus
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from src.configs.logger_setup import logger
from src.domain.bot_service.functions import BotFunctions
from src.domain.buttons import check_group, start_sending_keyboard
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

		if message.chat.type == 'group' or message.chat.type == 'supergroup':
			await message.answer(f"ID этой группы: {message.chat.id}")
			logger.info("Бот стартанул в группе!")

		else:
			logger.info("Бот стартанул!")
			current_state = await state.get_state()

			if current_state is not None:
				await state.clear()

			await message.answer(
				f"Привет {message.from_user.first_name}.\n"
				f"Сперва добавьте Бот на вашу группу и сделайте Бота администратором группы",
				reply_markup=check_group,
				parse_mode=ParseMode.MARKDOWN
			)


	@staticmethod
	async def get_group_id(message: Message, state: FSMContext) -> None:
		await state.set_state(FSMAdmin.telegram_group_id)

		await message.answer(
			"Отправьте ID Группы который добавили этот бот\n\n"
			"Чтобы узнать ID вашей группы, отправьте '/start' на вашу группу.",
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


