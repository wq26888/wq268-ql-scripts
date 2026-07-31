# 脚本来源与修改说明

本仓库用于保存个人实际运行并持续维护的青龙脚本。以下记录直接来源、已知的更早来源、主要修改和许可情况。

## 69 云签到

- 文件：`69yun/69yun_checkin.py`
- 原始来源：不详
- 类型：早期 SSPanel 类通用机场签到脚本
- 当前维护：Session 管理 Cookie、网络重试、代理、多机场、多账号、用户信息提取及公共通知
- 许可说明：不对来源不明的旧有部分主张原创或重新许可

## iKuuu 签到

- 文件：`ikuuu/ikuuu_checkin.py`
- 直接来源：[agluo/ql-script-hub](https://github.com/agluo/ql-script-hub/blob/master/ikuuu_checkin.py)
- 更早来源：[bighammer-link/jichang_dailycheckin](https://github.com/bighammer-link/jichang_dailycheckin)
- 当前维护：Cookie 登录、可配置域名、公共通知和登录兼容处理
- 上游许可：MIT License

## 夸克签到

- 文件：`quark/quark_signin.py`
- 直接来源：[agluo/ql-script-hub](https://github.com/agluo/ql-script-hub/blob/master/quark_signin.py)
- 当前维护：接入仓库公共通知模块
- 上游许可：MIT License

## 天翼云盘签到

- 文件：`cloud189/cloud189_checkin_v2.py`
- 直接来源：[agluo/ql-script-hub](https://github.com/agluo/ql-script-hub/blob/master/ty_netdisk_checkin.py)
- 上游文件注明的早期来源：[吾爱破解帖子](https://www.52pojie.cn/thread-1231190-1-1.html)
- 当前维护：基于旧版实现大幅重构，重新适配 2026 年登录认证、参数解析、多账号运行、异常处理和公共通知
- 许可说明：`agluo/ql-script-hub` 使用 MIT License；更早论坛代码未发现明确的独立许可声明

## GLaDOS 签到

- 文件：`glados/checkin.py`
- 原作者署名：Hennessey
- 上游项目：[RaineaAN/GLaDOS_Checkin_ql](https://github.com/RaineaAN/GLaDOS_Checkin_ql)
- 说明：项目原地址为 `hennessey-v/GLaDOS_Checkin_ql`，目前 GitHub 已重定向到上述地址
- 当前维护：更新服务域名、接口返回解析并接入仓库公共通知模块
- 上游许可：Apache License 2.0

## 公共模块与文档

- `common/notify.py`：从现有脚本的 Bark、Telegram 通知逻辑抽取并重新整理
- `README.md`、`ENVIRONMENT.md`、`TASKS.md`：本仓库整理维护
- 上述新增内容适用根目录 `LICENSE` 中限定范围的 MIT License

## 第三方许可副本

- `licenses/MIT-agluo.txt`
- `licenses/MIT-bighammer-link.txt`
- `licenses/Apache-2.0.txt`
