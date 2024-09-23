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
	async def get_wall(group_id: int) -> dict:
		url = settings.BASE_URL + "wall.get"
		params = {
			"access_token": settings.VK_APP_SERVICE_KEY,
			"owner_id": -group_id,
			"v": settings.VK_API_VERSION,
			"count": 1
		}

		async with aiohttp.ClientSession() as session:
			async with session.get(url, params=params, ssl=False) as response:
				server_data = await response.json()

		return server_data


	async def send_photo_from_album(self, event: dict, chat_id: int) -> None:

		photo_url = event["object"]["orig_photo"]["url"]
		description = event["text"]

		await self.bot.send_photo(
			chat_id=-chat_id, photo=URLInputFile(photo_url),
			caption=f"<b>{description}</b>",
			parse_mode="HTML"
		)

		logger.info("New photo from album sent successfully")


	async def send_photo_from_wall(self, event: dict, attachment: dict, chat_id: int) -> None:

		photo_url = attachment["photo"]["orig_photo"]["url"]
		description = event["text"]

		await self.bot.send_photo(
			chat_id=-chat_id, photo=URLInputFile(photo_url),
			caption=f"<b>{description}</b>",
			parse_mode="HTML"
		)

		logger.info("New photo from wall sent successfully")


	async def send_message_text(self, event: dict, chat_id: int) -> None:
		text = event["text"]

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

			logger.info("Опрос отправлено!")
		except Exception as e:
			logger.error(f"Неизвестный ошибка: {e}")


	async def send_location_service(self, event: dict, chat_id: int) -> None:
		coordinates = event['geo']['coordinates'].split()
		latitude = float(coordinates[0])
		longitude = float(coordinates[1])

		await self.bot.send_location(chat_id=-chat_id, latitude=latitude, longitude=longitude)

		logger.info("Локация отправлено!")


	async def send_document_service(self, attachment: dict, text: Optional[str], chat_id: int) -> None:
		doc_url = attachment["doc"]["url"]
		file_name = attachment["doc"]["title"]

		await self.bot.send_document(
			chat_id=-chat_id,
			document=URLInputFile(doc_url, filename=file_name),
			caption=text
		)

		logger.info("Новый файл отправлено!")


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
		if "geo" in event:
			await self.send_location_service(event, chat_id)

		elif "text" in event and not event["attachments"]:
			logger.info("Received a text message")
			await self.send_message_text(event, chat_id)

		elif "attachments" in event and event["attachments"]:
			for attachment in event["attachments"]:
				attachment_type = attachment["type"]

				if event["type"] == "photo_new":
					await self.send_photo_from_album(event, chat_id)

				if attachment_type == "photo":
					await self.send_photo_from_wall(event, attachment, chat_id)

				elif attachment_type == "poll":
					await self.send_pool_service(attachment, chat_id)

				elif attachment_type == "doc":
					await self.send_document_service(attachment, event["text"], chat_id)

				else:
					logger.info(f"Unknown type: {attachment_type}")

		else:
			logger.info("It's not clear")


