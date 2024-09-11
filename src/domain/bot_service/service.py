from aiogram.enums import ParseMode
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from src.configs.logger_setup import logger
from src.domain.bot_service.functions import BotFunctions
from src.domain.buttons import check_group, start_sending_keyboard
from src.domain.bot_service.models import FSMAdmin
from src.domain.buttons import choice_group
from src.domain.vk_bot_service.service import VkBotService


class BotService(BotFunctions, VkBotService):

	def __init__(self, bot: Bot, dp: Dispatcher) -> None:
		BotFunctions.__init__(self, bot, dp)
		VkBotService.__init__(self, bot)
		self.bot = bot
		self.dp = dp


	@staticmethod
	async def start_bot_service(message: Message, state: FSMContext) -> None:
		logger.info("Бот стартанул!")

		if message.chat.type == 'group' or message.chat.type == 'supergroup':
			await message.answer(f"ID этой группы: {message.chat.id}")
			logger.info("Бот стартанул в группе!")

		else:
			current_state = await state.get_state()

			if current_state is not None:
				await state.clear()

			await message.answer(
				f"Привет {message.from_user.first_name}.\n"
				f"Сперва добавьте Бот на вашу группу",
				reply_markup=check_group,
				parse_mode=ParseMode.MARKDOWN
			)


	@staticmethod
	async def get_group_id(message: Message, state: FSMContext) -> None:
		await state.set_state(FSMAdmin.telegram_group_id)

		if message.chat.type != 'group':
			await message.answer(
				"Отправьте ID Группы который добавил этот бот\n\n"
				"Чтобы узнать ID вашей группы, отправьте '/start' на вашу группу.",
				parse_mode=ParseMode.MARKDOWN, reply_markup=ReplyKeyboardRemove()
			)


	async def check_group(self, message: Message, state: FSMContext) -> None:
		group_id = await self.is_integer_string(message.text)

		if group_id:
			await self.is_bot_in_group(message, group_id, state)

		else:
			await message.answer("Отправьте корректный ID Группы.\n"
			                     "Только цифры!")


	async def is_bot_in_group(self, message: Message, group_id: int, state: FSMContext) -> None:
		try:
			chat = await self.bot.get_chat(-group_id)
			await message.answer(f"Бот добавлен в группу: {chat.title}", parse_mode=ParseMode.MARKDOWN)

			await state.update_data(telegram_group_id=message.text)
			await state.set_state(FSMAdmin.vk_group_id)

			await message.answer("Теперь отправьте ID группы Vk")

		except TelegramBadRequest as e:
			logger.error(f"{e}")
			await message.answer("Некорректный ID группы. Пожалуйста, проверьте и попробуйте снова.")

		except Exception as e:
			logger.error(f"Произошла ошибка: {str(e)}")


	async def get_vk_group_id_service(self, message: Message, state: FSMContext) -> None:
		vk_group_id = await self.is_integer_string(message.text)

		if vk_group_id:
			group_name = await self.check_vk_group(vk_group_id)

			if group_name:
				await message.answer(f"Корректный ID Группы.\n"
				                     f"Имя группы {group_name}.")

				await message.answer("Это ваша группа?\n"
				                     "Если нет то нажмите на кнопку 'Другое'", reply_markup=choice_group)

				await state.update_data(vk_group_id=vk_group_id)
				await state.set_state(FSMAdmin.vk_group_token)

		else:
			await message.answer("Некорректный ID группы. Пожалуйста, проверьте и попробуйте снова.")


	@staticmethod
	async def group_choice_service(message: Message, state: FSMContext) -> None:
		if message.text == "Другое":
			await message.answer("Введите ID группы заново:", reply_markup=ReplyKeyboardRemove())
			await state.set_state(FSMAdmin.vk_group_id)

		elif message.text == "Да":
			await message.reply(
				"Хорошо, отправьте ключ доступа Long Poll API из группы Vk.\n"
				"\n"
				"Если не знаете что это такое то можете прочитать вот здесь👇👇👇", reply_markup=ReplyKeyboardRemove())

			await message.answer(
				"https://dev.vk.com/ru/api/access-token/"
				"getting-started#%D0%9A%D0%BB%D1%8E%D1%87%20%D0%B4%D0%BE%D1%81%D1%82%D1%83%D0%BF%"
				"D0%B0%20%D1%81%D0%BE%D0%BE%D0%B1%D1%89%D0%B5%D1%81%D1%82%D0%B2%D0%B0"
			)

			await state.set_state(FSMAdmin.vk_group_token)


	async def get_long_pool_key(self, message: Message, state: FSMContext) -> None:
		data = await state.get_data()
		vk_group_id = data.get('vk_group_id')

		long_poll_data = await self.get_server_key(vk_group_id, message.text)

		if "response" in long_poll_data:
			await message.answer(
				"Вы верно передали все параметры теперь можете начать отправления сообщений",
				reply_markup=start_sending_keyboard
			)

			long_poll_url = long_poll_data["response"]["server"]
			long_poll_token = long_poll_data["response"]["key"]
			ts = long_poll_data["response"]["ts"]

			await state.update_data(
				vk_group_token=message.text, vk_long_poll_server_url=long_poll_url,
				vk_long_poll_server_token=long_poll_token, ts=ts, send_status=False
			)

			await state.set_state(FSMAdmin.start)

		else:
			logger.warn("Incorrect Token")
			await message.answer("Неправильный токен доступа. Пожалуйста, проверьте и попробуйте снова.")






