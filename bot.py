import asyncio
import json
import pprint
import datetime
from loguru import logger
from creart import create
from graia.ariadne.connection.config import (
    HttpClientConfig,
    WebsocketClientConfig,
    config,
)
from graia.broadcast import Broadcast
from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, Source, At, Image, App
from graia.ariadne.model import Friend, Group, Member
from graia.ariadne.event.mirai import NudgeEvent
#import requests
import debug
from features import soutu, tianqi, bilibili, goldprice, xinwen
punc = '~`!#$%^&*()_+-=|\';":/.,?><~·！@#￥%……&*（）--+-="：’；、。，？》《{}'
loop = asyncio.new_event_loop()



zxzzQun = 456850568 # 专心致志群
WuYongQun = 736964479 # zxz无用传输群 群号
zxzyxyQun = 762751056
NewsQQ_yijie = 2272145754
NewsQQ_phd = 1114945708
yjs_dormQun = 994531378
bk_dormQun = 904916898
manage_group = [zxzzQun, WuYongQun, zxzyxyQun]
xinwen_member = [NewsQQ_yijie, NewsQQ_phd]
xinwen_group = [WuYongQun, yjs_dormQun, bk_dormQun]
# debug
# xinwen_member.append(1025434914)


#logger.remove()
logger.add("logs/file_{time}.log",level="INFO")

bcc = create(Broadcast)
app = Ariadne(
    connection=config(
        2675621172,  # 你的机器人的 qq 号
        "myzxzGraiaxVerifyKey",  # 填入你的 mirai-api-http 配置中的 verifyKey
        # 以下两行（不含注释）里的 host 参数的地址
        # 是你的 mirai-api-http 地址中的地址与端口
        # 他们默认为 "http://localhost:8080"
        # 如果你 mirai-api-http 的地址与端口也是 localhost:8080
        # 就可以删掉这两行，否则需要修改为 mirai-api-http 的地址与端口
        # HttpClientConfig(host="http://11.45.1.4:19810"),
        # WebsocketClientConfig(host="http://11.45.1.4:19810"),
    ),
)




@bcc.receiver("FriendMessage")
async def friend_message_listener(message: MessageChain, app: Ariadne, friend: Friend):
    
    if "查询事件总数" in message.display:
        pprint.pprint(asyncio.all_tasks())
        
        await app.send_message(friend, MessageChain(str(asyncio.all_tasks())))
        return
    if "执行" in message.display:
        exec_str = message.display[2:]
        ret_str = eval(exec_str)
        print(f"{message.display}的结果:{ret_str}")
        await app.send_message(friend, MessageChain(f"{message.display}的结果:{ret_str}"))
        return
    #b站推送
    if "开启推送" in message.display:
        bilibili.keep_working = True
        element = message.display[4:]
        element = element.split('&')
        name = element[0]
        start = 1
        if len(element) > 1:
            start = int(element[1])
        if start >= 10:
            await app.send_message(friend, MessageChain("参数不合法,起始参数需<10"))
            return
        await bilibili.main(app, name, start)
        return 
    if "关闭b站推送" in message.display:
        bilibili.keep_working = False
        return
    if "金价推送" in message.display:
        await goldprice.main(app, friend)
        return
    if "实时金价" in message.display:
        await goldprice.ask(app, friend)
        return
    if "关闭金价推送" in message.display:
        goldprice.keep_working = False
        return
    if "开启易姐新闻" in message.display:
        group = message.display.split(" ")[1:]
        group = [int(x) for x in group]
        if len(group) == 0:            
            await xinwen.main(app, xinwen_group)
        else:
            await xinwen.main(app, group)
        return
    print(":::,",message.display)
    #receive_data = requests.get("http://api.qingyunke.com/api.php", {'key': 'free', 'appid':0, 'msg': message.display})#这里使用了网站提供的api得到机器人说的话，s是你对机器人说的话
    #receive_data.encoding = 'utf8'#设置编码，否则可能会乱码
    #receive_data = receive_data.json()#解析数据为json
    session = Ariadne.service.client_session
    async with session.get(f"http://api.qingyunke.com/api.php?key=free&appid=0&msg={message.display}") as r:
        data_bytes = await r.read()  
    data = json.loads(data_bytes)
    print(data)
    #print('菲菲：', data['content'])
    await app.send_message(friend, MessageChain([Plain(data['content'])]))
    
    # 实际上 MessageChain(...) 有没有 "[]" 都没关系


@bcc.receiver("GroupMessage")
async def group_message_listener(app: Ariadne, group: Group, message: MessageChain, member: Member, source: Source):

    await soutu.listen(app, group, message, member, source)
    await tianqi.listen(app, group, message, member, source)
    
    current_time = datetime.datetime.now()
    now_hour = current_time.hour
    now_minute = current_time.minute
    # print(member.id)
    # print(f"{now_hour}点{now_minute}分")
    # for elem in message.content:
    #     print("element type:", elem.type)
    #     print(elem)
       
    #     print("str:", str(elem.dict()))
    #     print(elem.display)
    #     print(elem.as_persistent_string())
    #     # print(elem.json())
    #     print("在里面吗", "睡前消息" in str(elem.dict()))
    #     print("在里面吗", "睡前消息" in elem.dict())
    #     print()
    if member.id in xinwen_member:
        if message.get(At) != []:
            return
        if False:
            pass
        #易姐的Cirno每天上午九点发新闻，图片的形式
        #elif member.id == NewsQQ_yijie:
        #    if not (now_hour != 9 and now_minute <= 5) or message.get(Image) == []:
        #        return
        else:
            if message.get(App) == [] or "睡前消息" not in str(message.get(App)[0].dict()):
                return
        await app.send_group_message(WuYongQun, MessageChain(
            f"来自QQ:{member.id}的每日新闻！"
        ) + message)


            
    # await app.send_group_message(WuYongQun, MessageChain(
    #     f"不要说{message.display}，来听听歌吧！"
    # ))
    #print("执行结束")

'''
@bcc.receiver(NudgeEvent)
async def getup(app: Ariadne, event: NudgeEvent):
    if event.context_type == "group":
        await app.send_group_message(event.group_id, MessageChain("你戳我干啥？"))
    else:
        await app.sendFriendMessage(event.friend_id, MessageChain("你戳我干啥？"))
'''

app.launch_blocking()

