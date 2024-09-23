from aiogram.fsm.state import State, StatesGroup
from pydantic import BaseModel


class FSMAdmin(StatesGroup):
	telegram_group_id = State()
	vk_group_id = State()
	yes_or_no = State()
	start_sending = State()
	stop_sending = State()


class GroupInformation(BaseModel):
	tel_group_id: int
	vk_group_id: int
	last_post_id: int | None = None
	send_status: bool = False

