# 脚本来源

这些脚本不是全由我写的。下面把目前能查到的出处和我改过的地方记一下，免得以后自己也忘了。

## 69 云

文件是 `69yun/69yun_checkin.py`。

最早从哪里拿到的已经记不清了，看接口应该是很常见的 SSPanel 类机场签到脚本。后来为了放在自己的青龙里跑，我加了 Session、失败重试、代理、多机场、多账号、流量信息和公共通知。

原作者和原仓库都没找到，所以旧代码不算作我的原创。

## iKuuu

我拿到的版本来自 [agluo/ql-script-hub](https://github.com/agluo/ql-script-hub/blob/master/ikuuu_checkin.py)，那个文件又注明原版来自 [bighammer-link/jichang_dailycheckin](https://github.com/bighammer-link/jichang_dailycheckin)。

我这边主要加了 Cookie 登录、可修改域名、公共通知，以及登录验证变化后的兼容处理。两个上游仓库都是 MIT License。

## 夸克

来源是 [agluo/ql-script-hub](https://github.com/agluo/ql-script-hub/blob/master/quark_signin.py)，MIT License。

这个改得不多，主要是接到现在共用的通知模块。

## 天翼云盘

最初用的是 [agluo/ql-script-hub](https://github.com/agluo/ql-script-hub/blob/master/ty_netdisk_checkin.py) 里的版本。它的文件头还提到了这篇 [吾爱破解帖子](https://www.52pojie.cn/thread-1231190-1-1.html)。

后来天翼的登录页面和流程变了，旧脚本已经不能用。现在这版重新处理了 2026 年的登录认证、页面参数、多账号、报错和通知，改动比较大，但仍保留旧版的一些基础结构，所以继续写明来源。

`agluo/ql-script-hub` 是 MIT License；更早的论坛代码没有找到单独的许可说明。

## GLaDOS

原作者署名是 Hennessey。原仓库地址后来转到了 [RaineaAN/GLaDOS_Checkin_ql](https://github.com/RaineaAN/GLaDOS_Checkin_ql)，使用 Apache License 2.0。

我改了新的服务域名、接口返回内容和公共通知。

## 我自己整理的部分

`common/notify.py` 是把几个脚本里的 Bark、Telegram 推送合到一起后重新整理的。README、环境变量和任务说明也是为了这个仓库写的。

上游许可原文放在 `licenses/`：

```text
MIT-agluo.txt
MIT-bighammer-link.txt
Apache-2.0.txt
```
