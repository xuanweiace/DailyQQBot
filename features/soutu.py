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
            if '我要看' in msg_str:
                # kantu()
                msg_str = msg_str.replace('我要看','').replace('。','').replace('！','')

                session = adapter_ctx.get().session
                async with session.get(f"https://ovooa.com/API/sgst/api.php?msg={msg_str}&type=text") as r:
                    url = await r.read()  
                url = url.decode()   
                print("url:", url)         

                await app.sendGroupMessage(group, MessageChain.create(
                    "伤心茄子想对你说：" + f"{msg_str}来啦！！！当当当当~"
                ))
                await app.sendGroupMessage(group, MessageChain.create(
                    Image(url=url)
                ))
                

        return