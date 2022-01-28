import asyncio
import json
from graia.broadcast import Broadcast

from graia.ariadne.context import adapter_ctx
from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, Source, At, Image
from graia.ariadne.model import Friend, Group, Member, MiraiSession
from graia.ariadne.event.mirai import NudgeEvent
#import requests
import debug
from features import soutu, tianqi, bilibili
punc = '~`!#$%^&*()_+-=|\';":/.,?><~·！@#￥%……&*（）--+-="：’；、。，？》《{}'
loop = asyncio.new_event_loop()

bcc = Broadcast(loop=loop)
app = Ariadne(
    broadcast=bcc,
    connect_info=MiraiSession(
        host="http://localhost:8080",  # 填入 HTTP API 服务运行的地址
        verify_key="ServiceVerifyKey",  # 填入 verifyKey
        account=2675621172,  # 你的机器人的 qq 号
    )
)


@bcc.receiver("FriendMessage")
async def friend_message_listener(message: MessageChain, app: Ariadne, friend: Friend):
    #b站推送
    if "开启推送" in message.asDisplay():
        bilibili.keep_working = True
        element = message.asDisplay()[4:]
        element = element.split('&')
        name = element[0]
        start = 1
        if len(element) > 1:
            start = int(element[1])
        if start >= 10:
            await app.sendMessage(friend, MessageChain.create("参数不合法,起始参数需<10"))
            return
        await bilibili.main(app, name, start)
        return 
    if "关闭推送" in message.asDisplay():
        bilibili.keep_working = False
        return


    print(":::,",message.asDisplay())
    #receive_data = requests.get("http://api.qingyunke.com/api.php", {'key': 'free', 'appid':0, 'msg': message.asDisplay()})#这里使用了网站提供的api得到机器人说的话，s是你对机器人说的话
    #receive_data.encoding = 'utf8'#设置编码，否则可能会乱码
    #receive_data = receive_data.json()#解析数据为json
    session = adapter_ctx.get().session
    async with session.get(f"http://api.qingyunke.com/api.php?key=free&appid=0&msg={message.asDisplay()}") as r:
        data_bytes = await r.read()  
    data = json.loads(data_bytes)
    print(data)
    #print('菲菲：', data['content'])
    await app.sendMessage(friend, MessageChain.create([Plain(data['content'])]))
    
    # 实际上 MessageChain.create(...) 有没有 "[]" 都没关系

zxzzQun = 456850568 # 专心致志群
WuYongQun = 736964479 # zxz无用传输群 群号
zxzyxyQun = 762751056
NewsQQ = 2272145754
news_group = [WuYongQun]

manage_group = [zxzzQun, WuYongQun, zxzyxyQun]
@bcc.receiver("GroupMessage")
async def group_message_listener(app: Ariadne, group: Group, message: MessageChain, member: Member, source: Source):

    await soutu.listen(app, group, message, member, source)
    await tianqi.listen(app, group, message, member, source)
    print(member.id)
    if member.id == 2272145754:
        await app.sendGroupMessage(WuYongQun, MessageChain.create(
            f"来自QQ:{member.id}的每日新闻！"
        ) + message)


            
    # await app.sendGroupMessage(WuYongQun, MessageChain.create(
    #     f"不要说{message.asDisplay()}，来听听歌吧！"
    # ))
    print("执行结束")

'''
@bcc.receiver(NudgeEvent)
async def getup(app: Ariadne, event: NudgeEvent):
    if event.context_type == "group":
        await app.sendGroupMessage(event.group_id, MessageChain.create("你戳我干啥？"))
    else:
        await app.sendFriendMessage(event.friend_id, MessageChain.create("你戳我干啥？"))
'''

loop.run_until_complete(app.lifecycle())

