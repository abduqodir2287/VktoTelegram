from aiogram.fsm.state import State, StatesGroup
from pydantic import BaseModel


class FSMAdmin(StatesGroup):
	telegram_group_id = State()
	vk_group_id = State()
	vk_group_token = State()
	start_sending = State()
	stop_sending = State()


class GroupInformation(BaseModel):
	tel_group_id: int
	vk_group_id: int
	vk_long_poll_token: str
	vk_long_poll_server_url: str | None = None
	vk_long_poll_server_token: str | None = None
	ts: int | None = None
	send_status: bool = False


