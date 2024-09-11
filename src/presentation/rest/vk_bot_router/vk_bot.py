from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.presentation.bot import bot
from src.domain.vk_bot_service.service import VkBotService
from src.domain.bot_service.models import FSMAdmin

vk_bot_router = Router(name=__name__)

bot_service = VkBotService(bot)


@vk_bot_router.message(FSMAdmin.start, F.text == "Начать отправку")
async def start_send_messages(message: Message, state: FSMContext) -> None:
	await bot_service.start_send_messages(message, state)


@vk_bot_router.message(FSMAdmin.stop, F.text == "Остановить отправку")
async def stop_sending(message: Message, state: FSMContext) -> None:
	await bot_service.stop_sending_messages(message, state)



