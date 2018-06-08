#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from threading import Timer
from wxpy import *
import requests,urllib
from PIL import Image
from io import BytesIO


#这里的二维码是用像素的形式打印出来！，如果你在win环境上运行，替换为  bot=Bot()
bot = Bot()
#bot = Bot(console_qr=2,cache_path="botoo.pkl")

def get_news():
    # 获取金山词霸每日一句，英文和翻译
    url = "http://open.iciba.com/dsapi/"
    r = requests.get(url)
    contents = r.json()['content']
    translation = r.json()['translation']
    fenxiang_img = r.json()['fenxiang_img']
    response = requests.get(fenxiang_img)
    image = Image.open(BytesIO(response.content))
    image.save('E:/weixin.jpg')
    return contents,translation

def send_news():
    my_friend = bot.friends().search(u'小妖')[0]
    my_friend.send(get_news()[0])
    my_friend.send(get_news()[1][5:])
    my_friend.send_image('E:/weixin.jpg')
    t = Timer(86400, send_news)
    t.start()

if __name__ == "__main__":
    send_news()
