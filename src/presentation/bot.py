from aiogram import Dispatcher, Bot, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.fsm.storage.redis import RedisStorage

from src.configs.config import settings
from src.domain.bot_service.service import BotService
from src.domain.bot_service.models import FSMAdmin

storage = RedisStorage.from_url(settings.REDIS_URL)

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher(storage=storage)

bot_service = BotService(bot, dp)


@dp.message(CommandStart())
async def start_bot(message: Message, state: FSMContext) -> None:
	await bot_service.start_bot_service(message, state)


@dp.message(F.text.in_({"Добавил"}), (F.chat.type != 'group') & (F.chat.type != 'supergroup'))
async def get_group_id(message: Message, state: FSMContext):
	await bot_service.get_group_id(message, state)


@dp.message(FSMAdmin.telegram_group_id, (F.chat.type != 'group') & (F.chat.type != 'supergroup'))
async def check_group(message: Message, state: FSMContext) -> None:
	await bot_service.check_group(message, state)


@dp.message(FSMAdmin.vk_group_id)
async def get_vk_group_id(message: Message, state: FSMContext) -> None:
	await bot_service.get_vk_group_id_service(message, state)


@dp.message(F.text.in_({"Другое", "Да"}), (F.chat.type != 'group') & (F.chat.type != 'supergroup'))
async def group_choice(message: Message, state: FSMContext):
	await bot_service.group_choice_service(message, state)


@dp.message(FSMAdmin.vk_group_token)
async def get_long_pool_key(message: Message, state: FSMContext) -> None:
	await bot_service.get_long_pool_key(message, state)


