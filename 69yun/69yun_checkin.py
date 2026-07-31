#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
69yun_multi_checkin.py

这是很早以前保存下来的通用机场签到脚本，原出处已经找不到了。
后来为了放进自己的青龙，改了网络请求、代理、重试、多账号和通知。

优化版：
- Session 自动管理 Cookie
- Retry 自动重试
- timeout=(5,30)
- 多机场、多账号
- common_notify 推送
"""
import os,time,random,re,sys
from pathlib import Path
from datetime import datetime,timedelta
from urllib.parse import quote

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "common"))
from notify import send as common_notify

def get_proxies():
    p=os.getenv("PROXY_URL","").strip()
    return {"http":p,"https":p} if p else None

def create_session():
    s=requests.Session()
    retry=Retry(total=3,connect=3,read=3,backoff_factor=1,
                status_forcelist=[500,502,503,504],
                allowed_methods=["GET","POST"])
    adapter=HTTPAdapter(max_retries=retry)
    s.mount("http://",adapter)
    s.mount("https://",adapter)
    return s

def fetch_user_info(session,domain,headers):
    try:
        r=session.get(f"{domain}/user",headers=headers,timeout=(5,20),proxies=get_proxies())
        if r.status_code!=200:
            return "❌ 用户信息获取失败\n"
        soup=BeautifulSoup(r.text,"html.parser")
        info={"到期时间":"未知","剩余流量":"未知"}
        for s in soup.find_all("script"):
            txt=s.string or ""
            if "Class_Expire" in txt:
                m1=re.search(r"'Class_Expire': '(.*?)'",txt)
                m2=re.search(r"'Unused_Traffic': '(.*?)'",txt)
                if m1: info["到期时间"]=m1.group(1)
                if m2: info["剩余流量"]=m2.group(1)
                break
        return f"到期时间：{info['到期时间']}\n剩余流量：{info['剩余流量']}\n"
    except Exception as e:
        return f"❌ 用户信息提取异常：{e}\n"

def checkin(account,url):
    session=create_session()
    headers={"User-Agent":"Mozilla/5.0","Accept":"application/json","Content-Type":"application/json"}
    try:
        print(f"[{account['user']}] 登录...")
        r=session.post(f"{url}/auth/login",json={"email":account["user"],"passwd":account["pass"],"remember_me":"on"},
                       headers=headers,timeout=(5,30),proxies=get_proxies())
        r.raise_for_status()
        print("登录成功，开始签到...")
        r=session.post(f"{url}/user/checkin",headers={"User-Agent":"Mozilla/5.0"},
                       timeout=(5,30),proxies=get_proxies())
        try:
            result=r.json().get("msg","未知")
        except Exception:
            result=f"HTTP {r.status_code}（非JSON）"
        info=fetch_user_info(session,url,{"User-Agent":"Mozilla/5.0"})
        msg=f"账号：{account['user'][:2]}****{account['user'][-3:]}\n{info}签到结果：{result}"
        print(msg)
        return msg
    except Exception as e:
        err=f"{account['user']} 签到异常：{e}"
        print(err)
        return err

def main():
    idx=1
    while True:
        url=os.getenv(f"AIRPORT{idx}_URL","").rstrip("/")
        if not url: break
        print(f"========== 机场{idx}: {url} ==========")
        n=1
        while True:
            u=os.getenv(f"AIRPORT{idx}_USER{n}")
            p=os.getenv(f"AIRPORT{idx}_PASS{n}")
            if not u or not p: break
            common_notify("69云签到",checkin({"user":u,"pass":p},url))
            time.sleep(random.randint(2,5))
            n+=1
        idx+=1

if __name__=="__main__":
    main()
