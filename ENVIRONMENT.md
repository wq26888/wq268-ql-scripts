# 环境变量

环境变量均在青龙面板中配置，仓库内不要填写真实值。

## 公共通知

| 变量名 | 说明 |
| --- | --- |
| `BARK_PUSH` | Bark key 或完整 Bark 服务地址 |
| `BOT_TOKEN` / `CHAT_ID` | Telegram Bot token 和会话 ID |
| `TG_BOT_TOKEN` / `TG_USER_ID` | Telegram 兼容变量名 |

## 公共代理

| 变量名 | 说明 |
| --- | --- |
| `PROXY_URL` | 优先使用的代理地址，例如 `http://127.0.0.1:7890` |
| `HTTPS_PROXY` | HTTPS 代理 |
| `HTTP_PROXY` | HTTP 代理 |
| `ALL_PROXY` | 通用代理 |

## 69云

| 变量名 | 说明 |
| --- | --- |
| `AIRPORT1_URL` | 第 1 个机场地址 |
| `AIRPORT1_USER1` | 第 1 个机场的第 1 个账号 |
| `AIRPORT1_PASS1` | 第 1 个机场的第 1 个密码 |

多账号可继续配置 `AIRPORT1_USER2`、`AIRPORT1_PASS2`；多机场可继续配置 `AIRPORT2_URL` 及对应账号。

## iKuuu

| 变量名 | 说明 |
| --- | --- |
| `IKUUU_BASE_URL` | 站点地址，不设置时使用脚本默认值 |
| `IKUUU_COOKIE` | 登录后的 Cookie；遇到网页登录验证时优先使用 |
| `IKUUU_EMAIL` | 登录邮箱 |
| `IKUUU_PASSWD` | 登录密码 |

## 夸克

| 变量名 | 说明 |
| --- | --- |
| `QUARK_COOKIE` | 夸克 Cookie；多账号用换行或 `&&` 分隔 |

## 天翼云盘

| 变量名 | 说明 |
| --- | --- |
| `TY_USERNAME` | 天翼云盘账号；多账号每行一个 |
| `TY_PASSWORD` | 天翼云盘密码；顺序与账号逐行对应 |
| `TY_LOGIN_VARIANTS` | 可选，登录参数兼容模式 |
| `TY_DEBUG` | 可选，设为 `true` 输出调试信息 |

## GLaDOS

| 变量名 | 说明 |
| --- | --- |
| `GR_COOKIE` | GLaDOS Cookie；多账号用换行或 `&` 分隔 |

## 随机延迟和隐私输出

| 变量名 | 说明 |
| --- | --- |
| `RANDOM_SIGNIN` | `true` 启用随机延迟，`false` 关闭 |
| `MAX_RANDOM_DELAY` | 最大随机延迟秒数 |
| `PRIVACY_MODE` | `true` 时隐藏日志中的部分账号信息 |
