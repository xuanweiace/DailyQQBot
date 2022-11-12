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


keep_working = True
async def main(app: Ariadne, friend: Friend):
    global keep_working
    keep_working = True
    await push_daily(app, friend)

    
async def push_daily(app: Ariadne, friend: Friend):
    global keep_working
    while keep_working :
        await app.send_message(friend, MessageChain(
            Image(url = "http://photo.zhijinwang.com/cn/live_charts/goldcny.gif")
        ))
        # await asyncio.sleep(60)
        await asyncio.sleep(86400)

async def ask(app: Ariadne, friend: Friend):
    await app.send_message(friend, MessageChain(
        Image(url = "http://photo.zhijinwang.com/cn/live_charts/goldcny.gif")
    ))