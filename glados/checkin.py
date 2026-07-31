#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File: checkin.py(GLaDOS签到)
Author: Hennessey
cron: 40 0 * * *
new Env('GLaDOS签到');
Update: 2023/7/27

Upstream:
https://github.com/RaineaAN/GlaDOS_Checkin_ql

这边改了新的服务域名、接口返回内容和公共通知。
上游使用 Apache License 2.0。
"""


import requests
import json
import os
import sys
import time
from pathlib import Path

# 获取GlaDOS账号Cookie
def get_cookies():
    if os.environ.get("GR_COOKIE"):
        print("已获取并使用Env环境 Cookie")
        if '&' in os.environ["GR_COOKIE"]:
            cookies = os.environ["GR_COOKIE"].split('&')
        elif '\n' in os.environ["GR_COOKIE"]:
            cookies = os.environ["GR_COOKIE"].split('\n')
        else:
            cookies = [os.environ["GR_COOKIE"]]
    else:
        from config import Cookies
        cookies = Cookies
        if len(cookies) == 0:
            print("未获取到正确的GlaDOS账号Cookie")
            return
    print(f"共获取到{len(cookies)}个GlaDOS账号Cookie\n")
    print(f"脚本执行时间(北京时区): {time.strftime('%Y/%m/%d %H:%M:%S', time.localtime())}\n")
    return cookies


# 加载通知服务
def load_send():
    common_path = Path(__file__).resolve().parents[1] / "common"
    sys.path.insert(0, str(common_path))
    try:
        from notify import send
        return send
    except Exception as e:
        print(f"加载通知服务失败：{e}")
        return None


# GlaDOS签到
def checkin(cookie):
    checkin_url= "https://glados.cloud/api/user/checkin"
    state_url= "https://glados.cloud/api/user/status"
    origin = "https://glados.cloud"
    useragent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"
    payload={
        'token': 'glados.cloud'
    }
    try:
        checkin = requests.post(checkin_url,headers={
            'cookie': cookie ,
            'origin':origin,
            'user-agent':useragent,
            'content-type':'application/json;charset=UTF-8'},data=json.dumps(payload))
        state =  requests.get(state_url,headers={
            'cookie': cookie ,
            'origin':origin,
            'user-agent':useragent})
    except Exception as e:
        print(f"签到失败，请检查网络：{e}")
        return None, None, None

    try:
        mess = checkin.json()['message']
        points = checkin.json()['points']
    except Exception as e:
        print(f"解析登录结果失败：{e}")
        return None, None

    return mess, points


# 执行签到任务
def run_checkin():
    contents = []
    cookies = get_cookies()
    if not cookies:
        return ""

    for cookie in cookies:
        ret, points = checkin(cookie)
        if not ret:
            continue

        content = f"账号：签到结果：{ret}\n获得点数：{points}\n"
        print(content)
        contents.append(content)

    contents_str = "".join(contents)
    return contents_str


if __name__ == '__main__':
    title = "GlaDOS签到通知"
    contents = run_checkin()
    send_notify = load_send()
    if send_notify:
        if contents =='':
            contents=f'签到失败，请检查账户信息以及网络环境'
            print(contents)
        send_notify(title, contents)
