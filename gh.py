# -*- coding: utf-8 -*-
import os
import sys
import json
import requests
from datetime import datetime, timedelta

'''
cron: 30 8-18/3 * * *
const $ = new Env("工会活动");
'''

# 获取WxPusher appToken  WxPusher_appToken
if "WxPusher_appToken" in os.environ:
    if len(os.environ["WxPusher_appToken"]) > 1:
        WxPusher_appToken = os.environ["WxPusher_appToken"]
else:
    print('未配置环境变量 WxPusher_appToken')
    sys.exit()

# 获取WxPusher uid  WxPusher_uids ','分隔
if "WxPusher_uids" in os.environ:
    if len(os.environ["WxPusher_uids"]) > 1:
        WxPusher_uids = os.environ["WxPusher_uids"].split(',')
else:
    print('未配置环境变量 WxPusher_uids')
    sys.exit()


def get_data():
    http_url = (r'https://zhghkgapi.hngh.org/openway/applet/appZH/active/getHomeActivityList?unionId=231555908549038080'
                r'&userId=')
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/122.0.0.0'
                      'Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows '
                      'WindowsWechat/WMPF WindowsWechat(0x63090c11)XWEB/11275'
    }
    try:
        r = requests.get(headers=headers, url=http_url)
        r.raise_for_status()  # 如果响应状态码不是200，将抛出HTTPError异常
        data = r.json().get('data')
    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)
        sys.exit()
    data = [x for x in data if "安阳" in x.get('unionName', '')]
    content = []
    current_time = datetime.now()
    for i in data:
        create_time = datetime.strptime(i['createTime'], '%Y-%m-%d %H:%M:%S')
        time_difference = current_time - create_time
        if time_difference < timedelta(hours=3):
            content.append(i)
    return content


def send_message(info):
    url = 'http://wxpusher.zjiecode.com/api/send/message'
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        'appToken': WxPusher_appToken,
        'content': info,
        'summary': '工会活动', # 消息摘要，显示在微信聊天页面或者模版消息卡片上，限制长度100，可以不传，不传默认截取content前面的内容。
        'contentType': 1,  # 内容类型 1表示文字 2表示html(只发送body标签内部的数据即可，不包括body标签) 3表示markdown
        # 'topicIds': [], # 发送目标的topicId，是一个数组！！！，也就是群发，使用uids单发的时候， 可以不传。
        'uids': WxPusher_uids  # 发送目标的UID，是一个数组。注意uids和topicIds可以同时填写，也可以只填写一个。
        # 'url': "" # 原文链接，可选参数
    }
    r = requests.post(headers=headers, url=url, data=json.dumps(data))
    if r.status_code == 200:
        print('信息发送成功,message:')
        print(info)
    else:
        print('信息发送失败,status_code:', r.status_code)


if __name__ == '__main__':
    message = ''
    infos = get_data()
    if len(infos) == 0:
        print('没有新活动')
        sys.exit()
    for index, i in enumerate(infos):
        message += '活动名称: {}\n'.format(i['name'])
        message += '活动时间: {}\n'.format(i['activeTime'])
        message += '活动创建时间: {}\n'.format(i['createTime'])
        # 判断是否为最后一项
        if index == len(infos) - 1:
            message += '活动发布单位: {}'.format(i['unionName'])
        else:
            message += '活动发布单位: {}\n'.format(i['unionName'])
            message += '---------------------------------\n'
    send_message(message)
