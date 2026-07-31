#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
cron "0 21 * * *"
new Env('iKuuu签到')

iKuuu 签到

我拿到的版本：
https://github.com/agluo/ql-script-hub/blob/master/ikuuu_checkin.py

更早的原版：
https://github.com/bighammer-link/jichang_dailycheckin

这边主要加了 Cookie 登录、可修改域名、公共通知和登录兼容处理。
两个上游仓库都是 MIT License，详情见 SOURCES.md。
"""

import os
import sys
import requests
import json
import re
import random
import time
from datetime import datetime
from pathlib import Path

hadsend = False
send = None
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "common"))
try:
    from notify import send
    hadsend = True
    print("✅ 已加载notify.py通知模块")
except ImportError:
    print("⚠️  未加载通知模块，跳过通知功能")

IKUUU_EMAIL = os.environ.get('IKUUU_EMAIL', '')
IKUUU_PASSWD = os.environ.get('IKUUU_PASSWD', '')
IKUUU_COOKIE = os.environ.get('IKUUU_COOKIE', '')
BASE_URL = os.environ.get('IKUUU_BASE_URL', 'https://ikuuu.win').rstrip('/')

max_random_delay = int(os.getenv("MAX_RANDOM_DELAY", "3600"))
random_signin = os.getenv("RANDOM_SIGNIN", "true").lower() == "true"
privacy_mode = os.getenv("PRIVACY_MODE", "true").lower() == "true"

LOGIN_URL = f'{BASE_URL}/auth/login'
CHECK_URL = f'{BASE_URL}/user/checkin'
USER_URL = f'{BASE_URL}/user'

HEADER = {
    'origin': BASE_URL,
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'referer': f'{BASE_URL}/user',
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'x-requested-with': 'XMLHttpRequest'
}

def mask_email(email):
    if not email or '@' not in email:
        return email
    if not privacy_mode:
        return email
    local, domain = email.split('@', 1)
    if len(local) <= 2:
        masked_local = '*' * len(local)
    else:
        masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
    return f"{masked_local}@{domain}"

def format_time_remaining(seconds):
    if seconds <= 0:
        return "立即执行"
    hours, rem = divmod(seconds, 3600)
    minutes, secs = divmod(rem, 60)
    if hours > 0:
        return f"{hours}小时{minutes}分{secs}秒"
    if minutes > 0:
        return f"{minutes}分{secs}秒"
    return f"{secs}秒"

def wait_with_countdown(delay_seconds, task_name):
    if delay_seconds <= 0:
        return
    print(f"{task_name} 需要等待 {format_time_remaining(delay_seconds)}")
    remaining = delay_seconds
    while remaining > 0:
        if remaining <= 10 or remaining % 10 == 0:
            print(f"{task_name} 倒计时: {format_time_remaining(remaining)}")
        sleep_time = 1 if remaining <= 10 else min(10, remaining)
        time.sleep(sleep_time)
        remaining -= sleep_time

def notify_user(title, content):
    if hadsend:
        try:
            send(title, content)
            print(f"✅ 通知发送完成: {title}")
        except Exception as e:
            print(f"❌ 通知发送失败: {e}")
    else:
        print(f"📢 {title}\n📄 {content}")

def load_cookie_to_session(session, cookie_str):
    if not cookie_str:
        return False

    cookie_str = cookie_str.strip()
    if cookie_str.lower().startswith("cookie:"):
        cookie_str = cookie_str.split(":", 1)[1].strip()

    session.headers.update({
        "cookie": cookie_str,
        "referer": f"{BASE_URL}/user"
    })
    return True

class IkuuuSigner:
    def __init__(self, email="", passwd="", index=1, cookie=""):
        self.email = email
        self.passwd = passwd
        self.index = index
        self.cookie = cookie
        self.session = requests.Session()
        self.session.headers.update(HEADER)

    def login_by_cookie(self):
        if not self.cookie.strip():
            return False, "未配置 Cookie"

        print("🍪 检测到 IKUUU_COOKIE，使用 Cookie 模式")
        load_cookie_to_session(self.session, self.cookie)
        print("✅ 已加载 Cookie，跳过网页登录验证，直接执行签到")
        return True, "Cookie 已加载"

    def login_by_password(self):
        print(f"🔐 正在登录账号: {mask_email(self.email)}")
        print(f"🌐 使用域名: {BASE_URL}")

        self.session.headers.update({
            "referer": f"{BASE_URL}/auth/login"
        })

        data = {
            'email': self.email,
            'passwd': self.passwd,
            'code': '',
            'remember_me': 'week'
        }

        response = self.session.post(LOGIN_URL, data=data, timeout=15)
        print(f"🔍 登录响应状态码: {response.status_code}")

        if response.status_code != 200:
            return False, f"登录请求失败，状态码: {response.status_code}"

        try:
            result = response.json()
            print(f"🔍 登录响应: {result}")
        except json.JSONDecodeError:
            print(f"❌ 登录响应格式错误: {response.text[:200]}")
            return False, "登录响应格式错误"

        if result.get("ret") == 1:
            print(f"✅ 登录成功: {result.get('msg', '登录成功')}")
            return True, "登录成功"

        return False, f"登录失败: {result.get('msg', '未知错误')}"

    def login(self):
        try:
            if self.cookie.strip():
                return self.login_by_cookie()

            if self.email.strip() and self.passwd.strip():
                return self.login_by_password()

            return False, "未配置 IKUUU_COOKIE，且邮箱或密码为空"

        except requests.exceptions.Timeout:
            return False, "登录请求超时"
        except requests.exceptions.ConnectionError:
            return False, "网络连接错误，请检查域名是否正确"
        except Exception as e:
            return False, f"登录异常: {str(e)}"

    def checkin(self):
        try:
            print("📝 正在执行签到...")

            self.session.headers.update({
                'origin': BASE_URL,
                'referer': f'{BASE_URL}/user',
                'accept': 'application/json, text/plain, */*',
                'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'x-requested-with': 'XMLHttpRequest'
            })

            response = self.session.post(CHECK_URL, timeout=15)
            print(f"🔍 签到响应状态码: {response.status_code}")

            if response.status_code != 200:
                print(f"❌ 签到响应内容: {response.text[:300]}")
                return False, f"签到请求失败，状态码: {response.status_code}"

            try:
                result = response.json()
                print(f"🔍 签到响应: {result}")
            except json.JSONDecodeError:
                print(f"❌ 签到响应格式错误: {response.text[:300]}")
                return False, "签到响应格式错误，可能 Cookie 无效或被验证页拦截"

            msg = result.get('msg', '签到完成')
            traffic_reward = self.extract_traffic_reward(msg, result)

            if result.get('ret') == 1:
                success_msg = "签到成功"
                if traffic_reward:
                    success_msg += f"，获得流量: {traffic_reward}"
                else:
                    success_msg += f"，{msg}"
                print(f"✅ {success_msg}")
                return True, success_msg

            if "已经签到" in msg or "already" in msg.lower() or "重复" in msg:
                already_msg = f"今日已签到: {msg}"
                print(f"📅 {already_msg}")
                return True, already_msg

            print(f"❌ 签到失败: {msg}")
            return False, f"签到失败: {msg}"

        except requests.exceptions.Timeout:
            return False, "签到请求超时"
        except requests.exceptions.ConnectionError:
            return False, "网络连接错误"
        except Exception as e:
            return False, f"签到异常: {str(e)}"

    def extract_traffic_reward(self, msg, result):
        patterns = [
            r'获得[了]?\s*(\d+(?:\.\d+)?)\s*([KMGT]?B)',
            r'奖励[了]?\s*(\d+(?:\.\d+)?)\s*([KMGT]?B)',
            r'增加[了]?\s*(\d+(?:\.\d+)?)\s*([KMGT]?B)',
            r'签到成功.*?(\d+(?:\.\d+)?)\s*([KMGT]?B)',
            r'(\d+(?:\.\d+)?)\s*([KMGT]?B).*?流量',
            r'流量.*?(\d+(?:\.\d+)?)\s*([KMGT]?B)',
            r'(\d+(?:\.\d+)?)\s*([KMGT]?B)',
        ]

        try:
            for pattern in patterns:
                match = re.search(pattern, msg, re.I)
                if match:
                    return f"{match.group(1)}{match.group(2)}"

            if isinstance(result, dict):
                for value in result.values():
                    if isinstance(value, str):
                        for pattern in patterns:
                            match = re.search(pattern, value, re.I)
                            if match:
                                return f"{match.group(1)}{match.group(2)}"
        except Exception as e:
            print(f"⚠️ 提取流量奖励异常: {e}")

        return None

    def main(self):
        print(f"\n==== ikuuu账号{self.index} 开始签到 ====")

        login_success, login_msg = self.login()
        if not login_success:
            return f"登录失败: {login_msg}", False

        time.sleep(random.uniform(1, 3))
        checkin_success, checkin_msg = self.checkin()

        account_name = mask_email(self.email) if self.email else f"Cookie账号{self.index}"
        final_msg = f"""🌟 ikuuu签到结果

👤 账号: {account_name}
🌐 域名: {BASE_URL}

📝 签到: {checkin_msg}
⏰ 时间: {datetime.now().strftime('%m-%d %H:%M')}"""

        print("✅ 任务完成" if checkin_success else "❌ 任务失败")
        return final_msg, checkin_success

def split_env(value):
    if not value:
        return []
    return [item.strip() for item in value.split(",,,,") if item.strip()] if ",,,," in value else [item.strip() for item in value.split(",") if item.strip()]

def main():
    print(f"==== ikuuu签到开始 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ====")
    print(f"🌐 当前域名: {BASE_URL}")
    print(f"🔒 隐私保护模式: {'已启用' if privacy_mode else '已禁用'}")

    if random_signin:
        delay_seconds = random.randint(0, max_random_delay)
        if delay_seconds > 0:
            print(f"🎲 随机延迟: {format_time_remaining(delay_seconds)}")
            wait_with_countdown(delay_seconds, "ikuuu签到")

    cookies = split_env(IKUUU_COOKIE)
    emails = split_env(IKUUU_EMAIL)
    passwords = split_env(IKUUU_PASSWD)

    if cookies:
        total_count = len(cookies)
        print(f"📝 共发现 {total_count} 个 Cookie 账号")
        signers = [
            IkuuuSigner(
                email=emails[i] if i < len(emails) else "",
                passwd=passwords[i] if i < len(passwords) else "",
                index=i + 1,
                cookie=cookie
            )
            for i, cookie in enumerate(cookies)
        ]
    else:
        if not emails or not passwords:
            error_msg = """❌ 未找到 IKUUU_COOKIE，也未找到 IKUUU_EMAIL 或 IKUUU_PASSWD

推荐配置:
IKUUU_COOKIE=浏览器登录后的 Cookie

备用配置:
IKUUU_EMAIL=邮箱
IKUUU_PASSWD=密码"""
            print(error_msg)
            notify_user("ikuuu签到失败", error_msg)
            return

        if len(emails) != len(passwords):
            error_msg = f"❌ 邮箱和密码数量不匹配：邮箱 {len(emails)} 个，密码 {len(passwords)} 个"
            print(error_msg)
            notify_user("ikuuu签到失败", error_msg)
            return

        total_count = len(emails)
        print(f"📝 共发现 {total_count} 个账号")
        signers = [
            IkuuuSigner(email=email, passwd=passwd, index=i + 1)
            for i, (email, passwd) in enumerate(zip(emails, passwords))
        ]

    success_count = 0

    for index, signer in enumerate(signers):
        try:
            if index > 0:
                delay = random.uniform(5, 15)
                print(f"⏱️ 随机等待 {delay:.1f} 秒后处理下一个账号...")
                time.sleep(delay)

            result_msg, is_success = signer.main()

            if is_success:
                success_count += 1

            notify_user(f"ikuuu账号{index + 1}签到{'成功' if is_success else '失败'}", result_msg)

        except Exception as e:
            error_msg = f"账号{index + 1}: 执行异常 - {str(e)}"
            print(f"❌ {error_msg}")
            notify_user(f"ikuuu账号{index + 1}签到失败", error_msg)

    print(f"\n==== ikuuu签到完成 - 成功{success_count}/{len(signers)} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ====")

def handler(event, context):
    main()

if __name__ == "__main__":
    main()
