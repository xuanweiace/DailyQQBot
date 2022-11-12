import errno
from logging import error
import aiohttp
import asyncio
import json
import time
from loguru import logger

from graia.broadcast import Broadcast

from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, Source, At, Image
from graia.ariadne.model import Friend, Group, Member
from graia.ariadne.event.mirai import NudgeEvent

from .configs import zxz

api_url = "http://118.31.18.68:8080/news/api/news-file/get?accessToken=eyJhbGciOiJIUzI1NiIsImtpZCI6ImRlZmF1bHQiLCJ0eXAiOiJKV1QifQ.eyJleHAiOjE2NjgwNzA3NTEsImZpbGVHVUlEIjoiWlY5bFdIU0Y2ZHd3d1puZSIsImlhdCI6MTY2ODA3MDQ1MSwiaXNzIjoidXBsb2FkZXJfYWNjZXNzX3Jlc291cmNlIiwidXNlcklkIjotNzM0MTcwNTUzNX0.5QUKo_6PJjL1Jf8_Px3t6K9W3rMj8bwR2sT0T2zANAo"

keep_working = True
async def main(app: Ariadne, group_list: list[int]):
    global keep_working
    keep_working = True
    await push_daily(app, group_list)

    
async def push_daily(app: Ariadne, group_list: Friend):
    global keep_working
    while keep_working :
        session = Ariadne.service.client_session
        async with session.get(api_url) as r:
            data = await r.text()  
            data_obj = json.loads(data)
            date = data_obj["result"]["date"]
            image_url = data_obj["result"]["data"][0]
        for group in group_list:
            await app.send_group_message(group, MessageChain(
                Image(url = image_url)
            ))
        # await asyncio.sleep(60)
        await app.send_friend_message(zxz["qq"], MessageChain("今日新闻推送已经发送完毕"))
        await asyncio.sleep(86400)
