from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.presentation.bot import bot
from src.domain.vk_router_service.service import VkRouterService
from src.domain.bot_service.models import FSMAdmin

vk_bot_router = Router(name=__name__)

router_service = VkRouterService(bot)


@vk_bot_router.message(FSMAdmin.start_sending, F.text == "Начать отправку")
async def start_send_messages(message: Message, state: FSMContext) -> None:
	await router_service.start_send_messages(message, state)


@vk_bot_router.message(FSMAdmin.stop_sending, F.text == "Остановить отправку")
async def stop_sending(message: Message, state: FSMContext) -> None:
	await router_service.stop_sending_messages(message, state)



