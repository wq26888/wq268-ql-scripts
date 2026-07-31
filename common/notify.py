#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
本仓库维护的公共通知模块。

从现有脚本中的 Bark、Telegram 通知逻辑抽取并重新整理，
支持 URL 编码和公共代理配置。许可范围见仓库 LICENSE。
"""

import os
from datetime import datetime, timedelta
from urllib.parse import quote

import requests


def get_proxy_url():
    return (
        os.getenv("PROXY_URL", "").strip()
        or os.getenv("HTTPS_PROXY", "").strip()
        or os.getenv("HTTP_PROXY", "").strip()
        or os.getenv("ALL_PROXY", "").strip()
    )


def get_proxies():
    proxy = get_proxy_url()
    if not proxy:
        return None
    return {"http": proxy, "https": proxy}


def _bark_url(title, content):
    bark_push = os.getenv("BARK_PUSH", "").strip()
    if not bark_push:
        return ""

    title_enc = quote(title, safe="")
    body_enc = quote(content, safe="")

    if bark_push.startswith("http://") or bark_push.startswith("https://"):
        return f"{bark_push.rstrip('/')}/{title_enc}/{body_enc}"

    return f"https://api.day.app/{bark_push}/{title_enc}/{body_enc}"


def send_bark(title, content):
    url = _bark_url(title, content)
    if not url:
        return False

    try:
        resp = requests.get(url, timeout=10, proxies=get_proxies())
        if resp.status_code == 200:
            print("✅ Bark 推送成功")
            return True
        print("❌ Bark 推送失败:", resp.text[:300])
    except Exception as exc:
        print("❌ Bark 推送异常:", exc)

    return False


def send_telegram(title, content):
    token = os.getenv("BOT_TOKEN", "").strip() or os.getenv("TG_BOT_TOKEN", "").strip()
    chat_id = os.getenv("CHAT_ID", "").strip() or os.getenv("TG_USER_ID", "").strip()
    if not token or not chat_id:
        return False

    now = datetime.utcnow() + timedelta(hours=8)
    text = f"{title}\n🕒 {now:%Y-%m-%d %H:%M:%S}\n\n{content}"
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data={"chat_id": chat_id, "text": text},
            timeout=10,
            proxies=get_proxies(),
        )
        if resp.status_code == 200:
            print("✅ Telegram 推送成功")
            return True
        print("❌ Telegram 推送失败:", resp.text[:300])
    except Exception as exc:
        print("❌ Telegram 推送异常:", exc)

    return False


def send(title, content):
    sent = False
    sent = send_bark(title, content) or sent
    sent = send_telegram(title, content) or sent
    if not sent:
        print("ℹ️ 未配置可用推送通道")
    return sent
