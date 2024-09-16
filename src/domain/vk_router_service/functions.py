from typing import Optional

from aiogram import Bot
from aiogram.types.input_file import URLInputFile
import aiohttp

from src.configs.config import settings
from src.configs.logger_setup import logger


class VkRouterFunctions:

	def __init__(self, bot: Bot):
		self.bot = bot

	@staticmethod
	async def get_server_key(group_id: int, group_access_token: str) -> dict:
		url = settings.BASE_URL + "groups.getLongPollServer"
		params = {
			"access_token": group_access_token,
			"group_id": group_id,
			"v": settings.VK_API_VERSION
		}

		async with aiohttp.ClientSession() as session:
			async with session.get(url, params=params, ssl=False) as response:
				server_data = await response.json()

		return server_data


	async def send_photo_from_album(self, event: dict, chat_id: int) -> None:

		photo_url = event["object"]["orig_photo"]["url"]
		description = event["object"]["text"]

		await self.bot.send_photo(
			chat_id=-chat_id, photo=URLInputFile(photo_url),
			caption=f"<b>{description}</b>",
			parse_mode="HTML"
		)

		logger.info("New photo from album sent successfully")


	async def send_photo_from_wall(self, event: dict, attachment: dict, chat_id: int) -> None:

		photo_url = attachment["photo"]["orig_photo"]["url"]
		description = event["object"]["text"]

		await self.bot.send_photo(
			chat_id=-chat_id, photo=URLInputFile(photo_url),
			caption=f"<b>{description}</b>",
			parse_mode="HTML"
		)

		logger.info("New photo from wall sent successfully")


	async def send_message_text(self, event: dict, chat_id: int) -> None:
		text = event["object"]["text"]

		text_parts = await self.text_split(text)

		for parts in text_parts:
			await self.bot.send_message(chat_id=-chat_id, text=parts)

			logger.info("New message sent successfully")

		logger.info("All parst of text sent successfully")

	async def send_pool_service(self, attachment: dict, chat_id: int) -> None:
		try:
			is_anonymous = attachment["poll"]["anonymous"]
			question = attachment["poll"]["question"]

			answers_list = []

			for answer in attachment["poll"]["answers"]:
				answers_list.append(answer)

			await self.bot.send_poll(
				chat_id=-chat_id,
				question=question,
				options=answers_list,
				is_anonymous=is_anonymous,
				type="regular"
			)
		except Exception as e:
			logger.error(f"Неизвестный ошибка: {e}")


	async def send_location_service(self, attachment: dict, chat_id: int) -> None:
		coordinates = attachment['geo']['coordinates'].split()
		latitude = float(coordinates[0])
		longitude = float(coordinates[1])

		await self.bot.send_location(chat_id=-chat_id, latitude=latitude, longitude=longitude)


	async def send_document_service(self, attachment: dict, text: Optional[str], chat_id: int) -> None:
		doc_url = attachment["doc"]["url"]
		file_name = attachment["doc"]["title"]

		await self.bot.send_document(
			chat_id=-chat_id,
			document=URLInputFile(doc_url, filename=file_name),
			caption=text
		)


	@staticmethod
	async def text_split(text: str) -> list:
		max_length = settings.TEXT_MAX_LENGTH
		strings_list = []

		while len(text) > max_length:
			split_index = text.rfind(' ', 0, max_length)

			strings_list.append(text[:split_index].strip())

			text = text[split_index:].strip()

		strings_list.append(text)

		return strings_list


	async def check_event(self, event: dict, chat_id: int) -> None:

		if "object" in event:
			obj = event["object"]

			if "text" in obj and not obj.get("attachments"):
				logger.info("Received a text message")
				await self.send_message_text(event, chat_id)

			elif "attachments" in obj and obj["attachments"]:
				for attachment in obj["attachments"]:
					attachment_type = attachment.get("type")

					if event["type"] == "photo_new":
						await self.send_photo_from_album(event, chat_id)

					if attachment_type == "photo":
						await self.send_photo_from_wall(event, attachment, chat_id)

					elif attachment_type == "poll":
						await self.send_pool_service(attachment, chat_id)

					elif attachment_type == "doc":
						await self.send_document_service(attachment, obj["text"], chat_id)

					elif attachment_type == "geo":
						await self.send_location_service(attachment, chat_id)

					else:
						logger.info(f"Unknown type: {attachment_type}")

			else:
				logger.info("It's not clear")


