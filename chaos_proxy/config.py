import sys
import aiohttp
import asyncio

SERVER = "http://localhost:2334"


async def set_config(key, value, server):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{server}/config/set/{key}/{value}") as response:
            return await response.text()


async def get_config(key, server):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{server}/config/get/{key}") as response:
            return await response.text()


async def main():
    if len(sys.argv) == 2:
        # get
        print(await get_config(sys.argv[1], SERVER))    # print it on the website
    if len(sys.argv) == 3:
        # set
        print(await set_config(sys.argv[1], sys.argv[2], SERVER))   # print it on the website


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())