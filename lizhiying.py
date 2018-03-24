#!/usr/bin/env python
# -*- coding:utf-8 -*-

import itchat,os
from itchat.content import *
import collections
from html.parser import HTMLParser
from xml.etree import ElementTree as et
import time,json,os,sys

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
    tmp_dict['MsgId'] = msg['MsgId']
    tmp_dict['FileName'] = msg['FileName']
    tmp_dict['Content'] = msg['Content']

    msg_store[CreateTime] = tmp_dict
    # 查看并清理
    clear_data(timeout)
@bot.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO])
def download_files(msg):
    msg["Text"](msg['FileName'])
    print(type(msg['FileName']))
    print(msg['FileName'])
    #msg.download(msg['FileName'])   #这个同样是下载文件的方式
    #将下载的文件发送给发送者
    # itchat.send('@%s@%s' % ('img' if msg['Type'] == 'Picture' else 'fil', msg["FileName"]), msg["FromUserName"])

def return_text_and_fn(content):
    root = et.fromstring(content)
    if root.tag == 'sysmsg':
        for child in root:
            if child.tag == 'revokemsg':
                for c in child:
                    if c.tag == 'msgid':
                        revokemsg_id = int(c.text)
                        for time, item in msg_store.items():
                            if int(item['MsgId']) == revokemsg_id:
                                revoke_msg = msg_store[time]
                                return revoke_msg

@bot.msg_register([TEXT,NOTE,MAP,CARD,SHARING,PICTURE,RECORDING,ATTACHMENT,VIDEO,SYSTEM],isFriendChat=True)
def text_reply(msg):
    Save_msg(msg)
    # 处理撤回的消息
    if msg['Type']=='Note' and '撤回' in msg['Text']:
        content = msg['Content']
        revoke_msg = return_text_and_fn(content)
        orginal_text = msg['Text'] +"\n"+"类型："+revoke_msg['Type']+"\n"
        if revoke_msg['Type']=='Text':
            bot.send(orginal_text+"内容："+revoke_msg['Text'],toUserName=msg['FromUserName'])
            bot.send(orginal_text + "内容：" + revoke_msg['Text'], toUserName='filehelper')
        elif revoke_msg['Type']=="Picture":
            fn = data_path+"/img/"+revoke_msg['FileName']
            revoke_msg['Text'](fn)
            bot.send('@msg@'+orginal_text.strip(), toUserName=msg['FromUserName'])
            bot.send('@img@' + fn, toUserName=msg['FromUserName'])
        elif revoke_msg['Type']=="Recording":
            fn = data_path+"/recording/"+revoke_msg['FileName']
            revoke_msg['Text'](fn)
            bot.send('@msg@'+orginal_text.strip(), toUserName=msg['FromUserName'])
            bot.send('@fil@' + fn, toUserName=msg['FromUserName'])




if __name__ == "__main__":
    if not os.path.exists(data_path):
        os.mkdir(data_path)
        os.mkdir(data_path+"/file")
        os.mkdir(data_path+"/img")
        os.mkdir(data_path + "/vieo")
        os.mkdir(data_path + "/recording")

    bot.run()