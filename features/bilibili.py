import aiohttp
import asyncio
import json
import time
from graia.broadcast import Broadcast

from graia.ariadne.context import adapter_ctx
from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, Source, At, Image
from graia.ariadne.model import Friend, Group, Member, MiraiSession
from graia.ariadne.event.mirai import NudgeEvent

from configs import zxz, yxy
zxzzQun = 456850568 # 专心致志群
WuYongQun = 736964479 # zxz无用传输群 群号
zxzyxyQun = 762751056
NewsQQ = 2272145754
botQQ = 2675621172
manage_group = [zxzzQun, WuYongQun, zxzyxyQun]


async def main(app: Ariadne, name:str, start:int):
    if name == 'zxz':
        await register_user(app, zxz, start)
    if name == 'yxy':
        await register_user(app, yxy, start)

keep_working = True
async def register_user(app: Ariadne, user:dict, start:int):
    last_bv = ''
    async with aiohttp.ClientSession() as session:
        while keep_working:
            data = await fetch(session, user['headers'], user['url'])
            data_obj = json.loads(data)
            try:
                assert len(data_obj["data"]["cards"]) == 20
            except Exception:
                #TODO:下一步这里加上app.sendMessgae到MAH
                print("长度不对，出错了,len=",len(data_obj["data"]["cards"]))   
                
            data = format_data(data_obj)

            print(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}, {user["name"]}的新信息如下：')
            new_bv = data[0]['short_link']
            new_bv = new_bv[new_bv.find('/BV'):].replace('/','')
            await exception_handle1(app, data)
            print("new_bv: ", new_bv, "实际: ", data[0]['short_link'])
            print("last_bv: ", last_bv)

            #理论上init bv 这一部分应该放到while循环外面，因为这部分只在第一次的时候用的到。
            init_bv = data[start]['short_link']
            init_bv = init_bv[init_bv.find('/BV'):].replace('/','')
            if last_bv == '':
                last_bv = init_bv
            # 增加对异常情况的过滤
            if bv_error(last_bv, data):
                last_bv = '' 
            for item in data:
                if last_bv in item['short_link']:
                    last_bv = new_bv
                    break
                print(item['title'], item['short_link'])
                
                await app.sendGroupMessage(user["sendgroup"], make_Chain(item))                
            print('-'*100)
            print('over')
            print("new_bv: ", new_bv)
            print("last_bv: ", last_bv)
            print('-'*100)
            
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
        if bv == data['bv']:
            return False
    # 说明待检测的bv不在爬取的数据中，会导致后面推送的时候不break，所有爬取的数据都推送过去了
    return True

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
    return ret_list
    
    
    
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
        print(f'格式有误.....:{e}')
        return 'error'

    return d

 
async def fetch(session, headers, url):
    
    async with session.get(url, headers = headers) as response:
        return await response.text()
    



           

#asyncio.run(main())