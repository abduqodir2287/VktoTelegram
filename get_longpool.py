import asyncio
import aiohttp

from src.configs.config import settings


async def get_server_key() -> str:
    url = settings.BASE_URL + "groups.getLongPollServer"
    params = {
        "access_token": "GROUP_ACCESS_TOKEN",
        "group_id": "GROUP_ID",
        "v": settings.VK_API_VERSION
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, ssl=False) as response:
            server_data = await response.json()

    return server_data["response"]["key"]


async def main():
    key = await get_server_key()
    long_poll_url = f"LONG_POLL_SERVER_URL?act=a_check&key={key}&ts=86&wait=3"
    async with aiohttp.ClientSession() as session:
        async with session.get(long_poll_url, ssl=False) as response:
            events = await response.text()
            with open("get_long_pool.json", "w", encoding="utf-8") as file:
                file.write(events)


asyncio.run(main())

