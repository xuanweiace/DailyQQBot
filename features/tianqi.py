import asyncio

from graia.broadcast import Broadcast

from graia.ariadne.context import adapter_ctx
from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, Source, At, Image
from graia.ariadne.model import Friend, Group, Member, MiraiSession
from graia.ariadne.event.mirai import NudgeEvent

zxzzQun = 456850568 # 专心致志群
WuYongQun = 736964479 # zxz无用传输群 群号
zxzyxyQun = 762751056
NewsQQ = 2272145754
manage_group = [zxzzQun, WuYongQun, zxzyxyQun]


async def listen(app: Ariadne, group: Group, message: MessageChain, member: Member, source: Source):
    if group.id in manage_group :
        if At(app.account) in message:

            filter_msg = message.include(Plain)
            msg_str = filter_msg.asDisplay()
            if '查询天气' in msg_str or '天气查询' in msg_str:
                location = msg_str[5:].strip()
                print(f"location:{location}")

                session = adapter_ctx.get().session
                async with session.get(f"http://ovooa.com/API/santq/api.php?msg={location}") as r:
                    data = await r.text()  

                await app.sendGroupMessage(group, MessageChain.create(
                    data
                ))
                

        return

async def aiohttptest():
    import aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://ovooa.com/API/santq/api.php?msg=济南") as response:
            data = await response.read()
            print(data)