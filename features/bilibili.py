import errno
from logging import error
import aiohttp
import asyncio
import json
import time
from loguru import logger

from graia.broadcast import Broadcast

from graia.ariadne.context import adapter_ctx
from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, Source, At, Image
from graia.ariadne.model import Friend, Group, Member, MiraiSession
from graia.ariadne.event.mirai import NudgeEvent

from .configs import zxz, yxy
zxzzQun = 456850568 # 专心致志群
WuYongQun = 736964479 # zxz无用传输群 群号
zxzyxyQun = 762751056
NewsQQ = 2272145754
botQQ = 2675621172
manage_group = [zxzzQun, WuYongQun, zxzyxyQun]


async def main(app: Ariadne, name:str, start:int):
    global keep_working
    keep_working = True
    if name == 'zxz':
        await register_user(app, zxz, start)
    if name == 'yxy':
        await register_user(app, yxy, start)

keep_working = True

@logger.catch
async def register_user(app: Ariadne, user:dict, start:int):
    #print("asyncio.current_task:", asyncio.current_task)
    global keep_working
    last_bv = ''
    record_list = [] # 暂时还是以last_bv这个下标来判断推送情况。但是为了防止出现，某次爬取到的信息是旧信息，因此加这个record_list记录已经推送过的BV号来兜底。
    async with aiohttp.ClientSession() as session:
        while keep_working:
            try:
                logger.info(f"这里是 {user['name']} 的b站推送功能----")
                data = await fetch(session, user['headers'], user['url'])
                data_obj = json.loads(data)
                try:
                    assert len(data_obj["data"]["cards"]) == 20
                except Exception:
                    #TODO:下一步这里加上app.sendMessgae到MAH
                    #NOTE: 虽然上面那个Try到了，但是万一是由于没有["cards"]字段造成的，则下面调用data_obj["data"]["cards"]
                    #NOTE: 还是会报错的呀，而且catch了之后就直接return掉就好了（当然，在此处是continue）
                    logger.info("长度不对，出错了,data_obj={}",data_obj)
                    #NOTE:刚开始这里忘加continue了，出现bug：爬取的时候只爬取到了一条信息，即len=1，如果不更新，则newbv跑到lastbv后面去了（即newbv是旧信息）因此需要认为这次爬取有误，不更新任何变量
                    continue
                    
                data = format_data(data_obj)
                
                logger.info(f"{user['name']}的新信息如下")
                #print(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}, {user["name"]}的新信息如下：')

                #new_bv的更新方式改变成直接取bv号
                # new_bv = data[0]['short_link']
                # new_bv = new_bv[new_bv.find('/BV'):].replace('/','')
                new_bv = data[0]['bv']
                await exception_handle1(app, data)
                logger.info("last_bv:{}, new_bv:{}, 实际: {}",last_bv,new_bv, data[0]['short_link'])

                #理论上init bv 这一部分应该放到while循环外面，因为这部分只在第一次的时候用的到。

                # init_bv = data[start]['short_link']
                # init_bv = init_bv[init_bv.find('/BV'):].replace('/','')
                init_bv = data[start]['bv']
                if last_bv == '':
                    last_bv = init_bv
                # 增加对异常情况的过滤
                if bv_error(last_bv, data):
                    app.sendGroupMessage(user["sendgroup"], f"https://b23.tv/{last_bv}找不到，已被删除！！")   
                    last_bv = data[0]['bv'] # 如果出现被删除的情况，则此次不推送
                    continue
                # if newbv_olderthan_lastbv(last_bv, new_bv, data):
                #     raise ValueError("newbv_olderthan_lastbv") 
                for item in data:
                    if last_bv in item['short_link']:
                        last_bv = new_bv
                        break
                    logger.info("得到新推送:{}, link:{}",item['title'], item['short_link'])
                    #print(item['title'], item['short_link'])
                    
                    #NOTE: 加一个兜底逻辑.
                    if item['bv'] in record_list:
                        continue

                    await app.sendGroupMessage(user["sendgroup"], make_Chain(item))     
                    
                    record_list.append(item['bv'])           
                
                logger.success("{}的b站推送处理完毕,over...new_bv:{}, last_bv:{}",user["name"], new_bv, last_bv)
                
            except Exception as e:
                logger.error(f"本次{user['name']}的b站推送失败了，原因是{repr(e)}，data的内容是{data}")
            await asyncio.sleep(60)




async def exception_handle1(app: Ariadne, data:dict):
    for item in data:
        bv = item['short_link']
        bv = bv[bv.find('/BV'):].replace('/','')
        if bv != item['bv']:

            await app.sendFriendMessage(botQQ, MessageChain.create("B站推送bv号和shortlink有误，具体信息如下：") + MessageChain.create(str(item)))

def bv_error(bv:str, data:dict):
    """
    检查bv是否在data中。
    为了过滤掉以下情景：
        一位up主发布了视频bv1，我做了推送，半分钟后他删除了视频。
        再过半分钟bot进行爬取数据，此时爬到的数据不包含了bv1，导致程序找不到推送起点，导致全部推送过来了。
    启发：
        发生异常等情况，可以选择推送到邮箱等方式，但不能初版本时直接从接收端做控制，给过滤掉，因为这样可能发现不了其他问题了。
        第二个启发是，不管什么功能（尤其是爬虫）前后，最好都要有预处理和后处理。可以先函数为空，但是最好先写上，这是一个好的框架。
        像我们这个bv_error检测，其实就算是对爬取的数据进行后处理了。
    """
    for item in data:
        if bv == item['bv']:
            return False
    # 说明待检测的bv不在爬取的数据中，会导致后面推送的时候不break，所有爬取的数据都推送过去了
    return True

# def newbv_olderthan_lastbv(last_bv, new_bv, data):
#     """
#     检测是否出现：new_bv排在last_bv后面，的情况。
#                 即new_bv是之前推送过的内容了（因为之前已经推送到的是last_bv）
#     检测方法：
#         顺序遍历data，如果先出现了new_bv，则没问题，如果先出现了
#     """
#     for item in data:
#         if new_bv == item['bv']:
#             return False
#         if last_bv == item['bv']:
#             return True

def make_Chain(d: dict)->MessageChain:
    c1 = MessageChain.create(
        f"B站推送：\n标题：{d['title']}, \nup主：{d['uname']}, \n分类：{d['tname']}\nu_info：{d['u_info']}\n链接：{d['short_link']}"
    )
    if 'video_fm' in d['img']:
        c1 = c1 + MessageChain.create(
            Image(url = d['img']['video_fm'])
        )
    return c1

def format_data(data_obj: dict)->list:
    ret_list = []
    cards = data_obj["data"]["cards"]
    for card in cards:
        ret = format_card(card)
        if ret != 'error': ret_list.append(ret)
    return ret_list # 格式化后，此时len不一定是20了
    
    
def format_card(card: dict)->dict:
    try:
        detail = json.loads(card['card']) # dict
        d = {}
        d['title'] = detail['title']
        d['bv'] = card['desc']['bvid'] # bv号
        d['uname'] = card['desc']['user_profile']['info']['uname']
        d['uid'] = card['desc']['user_profile']['info']['uid']
        detail = json.loads(card['card']) # dict
        d['short_link'] = detail['short_link']
        d['tname'] = detail['tname'] #分类
        d['u_info'] = detail['desc']
        d['img'] = {'u_face': detail['owner']['face'],
                    'video_fm': detail['pic']}
        #if 'first_frame' in detail: 
        #    d['img']['first_frame'] = detail['first_frame']
    except Exception as e:
        logger.error("b站爬取内容的格式有误,{}\ncard:{}",e,card)
        # print(f'格式有误.....:{e}')
        return 'error'

    return d

 
async def fetch(session, headers, url):
    
    async with session.get(url, headers = headers) as response:
        return await response.text()
    



           

#asyncio.run(main())