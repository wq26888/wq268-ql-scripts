#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
cron "1 16 * * *" script-path=xxx.py,tag=匹配cron用
new Env('天翼云盘签到')
2026-05 适配新版登录流程

版本：ty_netdisk_checkin_fixed_20260527_7

上游整理版：
https://github.com/agluo/ql-script-hub/blob/master/ty_netdisk_checkin.py

上游文件注明早期实现来自：
https://www.52pojie.cn/thread-1231190-1-1.html

当前版本基于旧版实现大幅重构，重新适配 2026 年登录认证、
参数解析、多账号运行、异常处理和公共通知。详细归属见仓库 SOURCES.md。
"""

import time
import re
import json
import base64
import hashlib
import urllib.parse
import hmac
import rsa
import requests
import random
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

SCRIPT_VERSION = "ty_netdisk_checkin_fixed_20260527_7"

# ---------------- 统一通知模块加载 ----------------
hadsend = False
send = None
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "common"))
try:
    from notify import send
    hadsend = True
    print("✅ 已加载notify.py通知模块")
except ImportError:
    print("⚠️  未加载通知模块，跳过通知功能")

# 随机延迟配置
max_random_delay = int(os.getenv("MAX_RANDOM_DELAY", "3600"))
random_signin = os.getenv("RANDOM_SIGNIN", "true").lower() == "true"
debug_enabled = os.getenv("TY_DEBUG", "false").lower() == "true"


def debug_log(message):
    if debug_enabled:
        print(message)


def format_time_remaining(seconds):
    if seconds <= 0:
        return "立即执行"
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours > 0:
        return f"{hours}小时{minutes}分{secs}秒"
    elif minutes > 0:
        return f"{minutes}分{secs}秒"
    else:
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
        print(f"📢 {title}")
        print(f"📄 {content}")


def pick_value(data, key, default=""):
    value = data.get(key)
    if value is None or value == "":
        return default
    return value


def form_value(value):
    """模拟浏览器 form 提交，避免 Python True 被编码成 True。"""
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return ""
    return str(value)


BI_RM = list("0123456789abcdefghijklmnopqrstuvwxyz")
B64MAP = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"


class TianYiYunPan:
    def __init__(self, username, password, index):
        self.username = username
        self.password = password
        self.index = index
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json, text/plain, */*",
        })

    def rsa_encode(self, pub_key, string):
        """新版前端 JSEncrypt.encrypt 返回 base64，不再做旧版 b64tohex。"""
        rsa_key = f"-----BEGIN PUBLIC KEY-----\n{pub_key}\n-----END PUBLIC KEY-----"
        pubkey = rsa.PublicKey.load_pkcs1_openssl_pem(rsa_key.encode())
        return base64.b64encode(rsa.encrypt(str(string).encode(), pubkey)).decode()

    def int2char(self, a):
        return BI_RM[a]

    def b64tohex(self, a):
        d = ""
        e = 0
        c = 0
        for i in range(len(a)):
            if list(a)[i] != "=":
                v = B64MAP.index(list(a)[i])
                if e == 0:
                    e = 1
                    d += self.int2char(v >> 2)
                    c = 3 & v
                elif e == 1:
                    e = 2
                    d += self.int2char(c << 2 | v >> 4)
                    c = 15 & v
                elif e == 2:
                    e = 3
                    d += self.int2char(c)
                    d += self.int2char(v >> 2)
                    c = 3 & v
                else:
                    e = 0
                    d += self.int2char(c << 2 | v >> 4)
                    d += self.int2char(15 & v)
        if e == 1:
            d += self.int2char(c << 2)
        return d

    def build_login_values(self, pub_key, pre, variant):
        username_b64 = self.rsa_encode(pub_key, self.username)
        password_b64 = self.rsa_encode(pub_key, self.password)

        if variant == "hex":
            return f"{pre}{self.b64tohex(username_b64)}", f"{pre}{self.b64tohex(password_b64)}"
        if variant == "plain_user":
            return self.username, f"{pre}{password_b64}"
        if variant == "preless":
            return username_b64, password_b64
        return f"{pre}{username_b64}", f"{pre}{password_b64}"

    def get_login_variants(self):
        variants = os.getenv("TY_LOGIN_VARIANTS", "hex").strip()
        return [v.strip() for v in variants.split(",") if v.strip()]

    def get_encrypt_conf(self, app_id="cloud", referer="https://open.e.189.cn/"):
        """从 encryptConf.do 获取加密配置（公钥、前缀）"""
        url = "https://open.e.189.cn/api/logbox/config/encryptConf.do"
        headers = {
            "Referer": referer,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        r = self.session.post(url, data={"appId": app_id}, headers=headers, timeout=15)
        data = r.json()
        if data.get("result") != 0:
            raise Exception(f"获取加密配置失败: {data}")
        return data["data"]

    def get_login_context(self):
        """
        跟随完整跳转链路，让 session 自动保存 cookie（LT、GUID、pageOp）。
        再调用 appConf.do 获取服务端登记的 returnUrl/paramId/state 等真实参数。
        """
        browser_id = hashlib.md5(f"{self.username}-{time.time()}-{random.random()}".encode()).hexdigest()
        redirect_url = "https://cloud.189.cn/web/redirect.html"
        login_action_url = (
            "https://cloud.189.cn/api/portal/loginUrl.action"
            f"?redirectURL={urllib.parse.quote(redirect_url, safe='')}"
            "&isLoginForRD=1"
            "&returnUrl="
            "&browser=true"
            "&browserType=82"
            "&defaultSaveNameCheck=uncheck"
            f"&browserId={browser_id}"
        )

        r = self.session.get(login_action_url, allow_redirects=True, timeout=15)
        final_url = r.url
        debug_log(f"账号{self.index}: 最终落地URL = {final_url[:100]}...")

        parsed = urllib.parse.urlparse(final_url)
        params = urllib.parse.parse_qs(parsed.query)

        app_id = params.get("appId", ["cloud"])[0]
        lt = params.get("lt", [None])[0]
        req_id = params.get("reqId", [None])[0]
        encrypt_url = params.get("encryptUrl", [""])[0]

        if not lt or not req_id:
            raise Exception(f"未能提取lt/reqId参数，final_url={final_url[:300]}")

        cookies = {c.name: c.value for c in self.session.cookies}
        debug_log(f"账号{self.index}: session cookies = {list(cookies.keys())}")

        auth_headers = {
            "Referer": final_url,
            "Content-Type": "application/x-www-form-urlencoded",
            "lt": lt,
            "reqId": req_id,
        }

        conf_resp = self.session.post(
            "https://open.e.189.cn/api/logbox/oauth2/appConf.do",
            data={"version": "2.0", "appKey": app_id},
            headers=auth_headers,
            timeout=15,
        )
        conf_json = conf_resp.json()
        debug_log(f"账号{self.index}: appConf 响应: {str(conf_json)[:300]}")

        if str(conf_json.get("result")) != "0" or not conf_json.get("data"):
            raise Exception(f"获取appConf失败: {conf_json}")

        return {
            "browserId": browser_id,
            "finalUrl": final_url,
            "appId": app_id,
            "lt": lt,
            "reqId": req_id,
            "encryptUrl": encrypt_url,
            "headers": auth_headers,
            "conf": conf_json["data"],
        }

    def login(self):
        """登录天翼云盘（新版流程）"""
        try:
            print(f"👤 账号{self.index}: 开始登录 {self.username}")

            context = self.get_login_context()
            conf = context["conf"]

            encrypt_conf = self.get_encrypt_conf(
                pick_value(conf, "appKey", context["appId"]),
                context["finalUrl"],
            )
            pub_key = encrypt_conf["pubKey"]
            pre = encrypt_conf.get("pre", "{NRP}")
            debug_log(f"账号{self.index}: 获取加密配置成功，前缀={pre}")
            debug_log(f"账号{self.index}: 获取登录参数成功，lt={context['lt'][:20]}...")

            variants = self.get_login_variants()
            debug_log(f"账号{self.index}: 登录加密变体 = {variants}")

            username_value, password_value = self.build_login_values(pub_key, pre, variants[0])

            needcaptcha_data = {
                "accountType": pick_value(conf, "accountType", "01"),
                "userName": username_value,
                "appKey": pick_value(conf, "appKey", context["appId"]),
            }
            needcaptcha_headers = context["headers"].copy()
            needcaptcha_headers["REQID"] = context["reqId"]
            needcaptcha_resp = self.session.post(
                "https://open.e.189.cn/api/logbox/oauth2/needcaptcha.do",
                data=needcaptcha_data,
                headers=needcaptcha_headers,
                timeout=15,
            )
            needcaptcha_text = needcaptcha_resp.text.strip()
            debug_log(f"账号{self.index}: needcaptcha 响应: {needcaptcha_text}")
            if needcaptcha_text == "1":
                print(f"❌ 账号{self.index}: 当前登录需要滑块/图形验证码，脚本暂不能自动完成")
                return False

            login_url = "https://open.e.189.cn/api/logbox/oauth2/loginSubmit.do"
            base_data = {
                "version": "v2.0",
                "apToken": "",
                "appKey": pick_value(conf, "appKey", context["appId"]),
                "pageKey": pick_value(conf, "pageKey", "default"),
                "accountType": pick_value(conf, "accountType", "01"),
                "captchaType": "",
                "validateCode": "",
                "smsValidateCode": "",
                "captchaToken": "",
                "returnUrl": urllib.parse.quote(
                    pick_value(conf, "returnUrl", "https://cloud.189.cn/web/redirect.html"),
                    safe="",
                ),
                "mailSuffix": pick_value(conf, "mailSuffix", ""),
                "dynamicCheck": "FALSE",
                "clientType": pick_value(conf, "clientType", "1"),
                "cb_SaveName": "3",
                "isOauth2": pick_value(conf, "isOauth2", "true"),
                "state": pick_value(conf, "state", ""),
                "paramId": pick_value(conf, "paramId", context["encryptUrl"]),
            }

            last_result = None
            for variant in variants:
                username_value, password_value = self.build_login_values(pub_key, pre, variant)
                data = base_data.copy()
                data["userName"] = username_value
                data["epd"] = password_value
                data = {k: form_value(v) for k, v in data.items()}

                debug_data = data.copy()
                debug_data["userName"] = debug_data["userName"][:20] + "..."
                debug_data["epd"] = debug_data["epd"][:20] + "..."
                debug_log(f"账号{self.index}: loginSubmit 变体={variant} 参数: {debug_data}")

                r = self.session.post(login_url, data=data, headers=context["headers"], timeout=15)
                result = r.json()
                last_result = result
                debug_log(f"账号{self.index}: loginSubmit 变体={variant} 响应: {result}")

                if result.get("result") == 0:
                    print(f"✅ 账号{self.index}: 登录成功")
                    redirect_url = result.get("toUrl", "")
                    if redirect_url:
                        self.session.get(redirect_url, timeout=15, allow_redirects=True)
                    return True

                # -149 是当前要定位的加密格式问题，继续试下一个变体。
                if result.get("result") != -149:
                    break

            msg = last_result.get("msg", str(last_result)) if last_result else "未知错误"
            print(f"❌ 账号{self.index}: 登录失败 - {msg}")
            return False

        except Exception as e:
            print(f"❌ 账号{self.index}: 登录异常 - {str(e)}")
            return False

    def sign_in(self):
        """执行签到"""
        try:
            print(f"🎯 账号{self.index}: 开始签到")
            rand = str(round(time.time() * 1000))
            sign_url = (
                "https://m.cloud.189.cn/userSign.action?"
                f"rand={rand}&clientType=TELEANDROID&version=8.6.3&model=SM-G930K"
            )
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Linux; Android 5.1.1; SM-G930K Build/NRD90M; wv) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 "
                    "Chrome/74.0.3729.136 Mobile Safari/537.36 "
                    "Ecloud/8.6.3 Android/22 clientId/355325117317828 "
                    "clientModel/SM-G930K imsi/460071114317824 clientChannelId/qq proVersion/1.0.6"
                ),
                "Referer": "https://m.cloud.189.cn/zhuanti/2016/sign/index.jsp?albumBackupOpened=1",
                "Accept-Encoding": "gzip, deflate",
            }
            response = self.session.get(sign_url, headers=headers, timeout=15)
            result = response.json()
            debug_log(f"账号{self.index}: sign 响应: {result}")

            if result.get("errorCode") or result.get("res_code"):
                return f"签到失败: {result}"

            netdiskBonus = result.get("netdiskBonus", 0)
            isSign = result.get("isSign", "true")
            if isSign is False or str(isSign).lower() == "false":
                status_msg = f"✅ 签到成功，获得 {netdiskBonus}M 空间"
                print(f"✅ 账号{self.index}: {status_msg}")
            else:
                status_msg = f"📅 今日已签到，获得 {netdiskBonus}M 空间"
                print(f"📅 账号{self.index}: {status_msg}")
            return status_msg
        except Exception as e:
            error_msg = f"签到异常: {str(e)}"
            print(f"❌ 账号{self.index}: {error_msg}")
            return error_msg

    def main(self):
        try:
            print(f"\n==== 账号{self.index} 开始执行 ====")
            print(f"🕐 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            if not self.login():
                error_msg = f"❌ 账号{self.index}: {self.username}\n登录失败，无法完成签到"
                print(error_msg)
                return error_msg, False
            sign_result = self.sign_in()
            result_msg = f"""☁️ 天翼云盘签到结果

👤 账号信息: {self.username}
📊 签到状态: {sign_result}
🕐 完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
            print("\n🎉 === 最终签到结果 ===")
            print(result_msg)
            print(f"==== 账号{self.index} 签到完成 ====\n")
            is_success = "签到成功" in sign_result or "已签到" in sign_result
            return result_msg, is_success
        except Exception as e:
            error_msg = f"❌ 账号{self.index}: 执行异常 - {str(e)}"
            print(error_msg)
            return error_msg, False


def main():
    print(f"🔖 脚本版本: {SCRIPT_VERSION}")
    print(f"==== 天翼云盘签到开始 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ====")

    if random_signin:
        delay_seconds = random.randint(0, max_random_delay)
        if delay_seconds > 0:
            signin_time = datetime.now() + timedelta(seconds=delay_seconds)
            print(f"🎲 随机模式: 延迟 {format_time_remaining(delay_seconds)} 后开始")
            print(f"⏰ 预计开始时间: {signin_time.strftime('%H:%M:%S')}")
            wait_with_countdown(delay_seconds, "天翼云盘签到")

    ty_username_env = os.getenv("TY_USERNAME", "")
    ty_password_env = os.getenv("TY_PASSWORD", "")

    if not ty_username_env or not ty_password_env:
        error_msg = "❌ 未找到TY_USERNAME或TY_PASSWORD环境变量"
        print(error_msg)
        notify_user("天翼云盘签到失败", error_msg)
        return

    usernames = [u.strip() for u in ty_username_env.replace("\r\n", "\n").split("\n") if u.strip()]
    passwords = [p.strip() for p in ty_password_env.replace("\r\n", "\n").split("\n") if p.strip()]

    if len(usernames) != len(passwords):
        error_msg = "❌ 用户名和密码数量不匹配"
        print(error_msg)
        notify_user("天翼云盘签到失败", error_msg)
        return

    print(f"📝 共发现 {len(usernames)} 个账号")

    success_accounts = 0
    all_results = []

    for index, (username, password) in enumerate(zip(usernames, passwords)):
        try:
            if index > 0:
                delay = random.uniform(10, 30)
                print(f"💤 随机等待 {delay:.1f} 秒后处理下一个账号...")
                time.sleep(delay)
            tianyi = TianYiYunPan(username, password, index + 1)
            result_msg, is_success = tianyi.main()
            all_results.append(result_msg)
            if is_success:
                success_accounts += 1
            title = f"天翼云盘账号{index + 1}签到{'成功' if is_success else '失败'}"
            notify_user(title, result_msg)
        except Exception as e:
            error_msg = f"❌ 账号{index + 1}: 处理异常 - {str(e)}"
            print(error_msg)
            all_results.append(error_msg)
            notify_user(f"天翼云盘账号{index + 1}签到失败", error_msg)

    if len(usernames) > 1:
        summary_msg = f"""☁️ 天翼云盘签到汇总

📊 总计处理: {len(usernames)}个账号
✅ 成功账号: {success_accounts}个
❌ 失败账号: {len(usernames) - success_accounts}个
📅 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

详细结果请查看各账号单独通知"""
        notify_user("天翼云盘签到汇总", summary_msg)
        print("\n📊 === 汇总统计 ===")
        print(summary_msg)

    print(f"\n==== 天翼云盘签到完成 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ====")


if __name__ == "__main__":
    main()
