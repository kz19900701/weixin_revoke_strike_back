#!/usr/bin/env python
# -*- coding:utf-8 -*-

import itchat,os
from itchat.content import *
import collections
from html.parser import HTMLParser
from xml.etree import ElementTree as et
import time

"""
    思路：
    监听lizhiying的msg，然后存在collections中，每条都存。然后根据收到的时间 超时10分钟 600 秒的 就删掉。撤回的消息不删
"""
# 初始化
bot = itchat.new_instance()
bot.auto_login(hotReload=True,enableCmdQR=2)
msg_store = collections.OrderedDict() # 存数据
timeout = 600 # 超时
data_path = "revoke_data" # 撤回的数据保存：图片



def clear_data(timeout):
    for k,v in msg_store.items():
        if ((time.time()-k)>timeout):
            a = msg_store.popitem(k)
            print(a)


# 存数据到内存
def Save_msg(msg):
    """
        功能
        1.存数据
        2.删除超过600s的数据
    :param msg:
    :return:
    """
    CreateTime = msg['CreateTime']
    tmp_dict = {}
    tmp_dict['MsgId']= msg['MsgId']
    tmp_dict['Type'] = msg['Type']
    tmp_dict['Text'] = msg['Text']
    tmp_dict['FromUserName'] = msg['FromUserName']
    tmp_dict['MsgId'] = msg['MsgId']

    msg_store[CreateTime] = tmp_dict
    # 查看并清理
    clear_data(timeout)

@bot.msg_register([TEXT,NOTE,MAP,CARD,SHARING,PICTURE,RECORDING,ATTACHMENT,VIDEO,SYSTEM],isFriendChat=True)
def text_reply(msg):
    Save_msg(msg)
    print(msg)
    print(type(msg))
    print(msg_store)
    print("====")
    # 处理撤回的消息
    if msg['Type']=='Note':
        content = msg['Content']
        revokemsg_id = 0
        root = et.fromstring(content)
        if root.tag == 'sysmsg':
            for child in root:
                if child.tag == 'revokemsg':
                    for c in child:
                        if c.tag == 'msgid':
                            revokemsg_id = int(c.text)
        revokemsg_text = ""
        revokemsg_toUserNme = ""
        for time,item in msg_store.items():
                if int(item['MsgId']) == revokemsg_id:
                    revokemsg_text = msg_store[time]['Text']
                    revokemsg_toUserNme = msg_store[time]['FromUserName']

        revokemsg_MSG = msg['Text']+"\n" +"内容："+revokemsg_text +"\n"
        print(revokemsg_MSG)
        bot.send(msg='@msg@'+revokemsg_MSG,toUserName=revokemsg_toUserNme)


if __name__ == "__main__":
    if not os.path.exists(data_path):
        os.mkdir(data_path)

    bot.run()